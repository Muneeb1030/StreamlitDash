import streamlit as st
import pandas as pd
import geopandas as gpd
import psycopg2
import os
import plotly.express as px
from pyproj import Proj, transform
import numpy as np
import os

global pois
global traffic

conn_string = os.getenv("COCKROACHDB_CONN")

def DatabaseInsertion():
    
    in_proj = Proj(init="epsg:3857") 
    out_proj = Proj(init="epsg:4326")
    # Creating Connection with PostgreSQL Database
    # conn = psycopg2.connect(
    #     host="localhost",
    #     database="Dataset",
    #     user="postgres",
    #     password="admin",
    #     port="5432"
    #     )
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor() # Cursor is used to interact with the database
    
    #Create a table in PostgreSQL database
    cur.execute('''
        CREATE TABLE IF NOT EXISTS POIs (
            id SERIAL PRIMARY KEY,
            type VARCHAR(100),
            longitude FLOAT,
            latitude FLOAT
        );
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Traffic (
            id SERIAL PRIMARY KEY,
            level INTEGER,
            longitude FLOAT,
            latitude FLOAT
        );
    ''')
    conn.commit()
          
    POICategories  = ['Education', 'FoodPoint', 'HealthPoint', 'Pharmacy','Bank','Masjid','PoliceStation','Shop','SuperMarket']
    # insert data into the table
    directory = "TrafficData/"
    files = os.listdir(directory) # List all the files in the directory
    shapefiles = [f for f in files if f.endswith(".shp")] # Filter out the shapefiles
    for idx, shapefile in enumerate(shapefiles): # Iterate over the shapefiles
        shapefile_path = os.path.join(directory, shapefile) # Get the path of the shapefile
        gdf = gpd.read_file(shapefile_path) # Read the shapefile using geopandas
        
        
        if 'geometry' in gdf.columns: # Check if the geometry column exists
            gdf['longitude'] = gdf['geometry'].x # Extract the longitude from the geometry column
            gdf['latitude'] = gdf['geometry'].y # Extract the latitude from the geometry column
            
        columns_to_keep = ['longitude', 'latitude'] # Columns to keep in the DataFrame
        gdf = gdf[columns_to_keep] # Keep only the required columns

        # Save to DataFrame
        df = pd.DataFrame(gdf)
        
        for i in range(len(df)):
            # Insert the data into the table but the projection of data will take time so i will not be able to run this code
            longitude, latitude = transform(in_proj, out_proj, float(df['longitude'][i]), float(df['latitude'][i]))

            cur.execute('''Insert into POIs (type, longitude, latitude) values (%s, %s, %s);''', (POICategories[idx], longitude, latitude))

        conn.commit()
        
    geojson_file = "TrafficData/TrafficHotspots/TrafficHotspots.geojson"
    gdf = gpd.read_file(geojson_file)
    # Create DataFrame with just the geometry column
    if 'geometry' in gdf.columns:
        gdf['longitude'] = gdf['geometry'].x
        gdf['latitude'] = gdf['geometry'].y

        columns_to_keep = ['level','longitude', 'latitude'] # Columns to keep in the DataFrame
        gdf = gdf[columns_to_keep]

        df = pd.DataFrame(gdf)

        for i in range(len(df)):
            level = int(df['level'][i]) # Level of Traffic
            longitude, latitude = transform(in_proj, out_proj, float(df['longitude'][i]), float(df['latitude'][i]))
            cur.execute('''Insert into Traffic (level, longitude, latitude) values (%s, %s, %s);''', (level, longitude, latitude))

        conn.commit()

    cur.close()
    conn.close()

# Function to retrieve data from the database
def DatabaseRetrieval():
    # Creating Connection with PostgreSQL Database
    # conn = psycopg2.connect(
    #     host="localhost",
    #     database="Dataset",
    #     user="postgres",
    #     password="admin",
    #     port="5432"
    #     )
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor() # Cursor is used to interact with the database
    
    # Select all the data from the tables
    cur.execute('''Select * from POIs;''')
    POIs = cur.fetchall() # Fetch all the data from the table
    
    cur.execute('''Select * from Traffic;''')
    Traffic = cur.fetchall()
    
    # Create DataFrames from the data with the columns names
    pois = pd.DataFrame(POIs, columns=['id', 'type', 'longitude', 'latitude'])
    traffic = pd.DataFrame(Traffic, columns=['id', 'level', 'longitude', 'latitude'])
    
    cur.close()
    conn.close()
    # Drop the id column, since it is just a serial number
    pois.drop(columns=['id'], inplace=True)
    traffic.drop(columns=['id'], inplace=True)
    
    # Return the DataFrames
    return pois, traffic

def Show_Home_Page():
    st.markdown("## Welcome to URBAN INSIGHTS")
    st.markdown("""
    **Urban Insights: Exploring Traffic Hotspots and Points of Interest** is an **interactive dashboard** designed to provide insights into urban dynamics by analyzing **Traffic Hotspots and Points of Interest (POIs)** within **Lahore, Punjab, Pakistan**.

    The dashboard enables users to explore the spatial distribution and relationships between traffic hotspots and various Points of Interest (POIs) such as education, healthcare, dining, shopping, etc. Each POI entry includes its type and geographic coordinates, providing valuable context for analyzing the accessibility and spatial distribution of essential services and recreational opportunities within Lahore.

    By integrating and visualizing these datasets, the dashboard aims to illuminate the intricate interplay between urban mobility, infrastructure, and community resources, fostering a deeper understanding of city life in Lahore and informing data-driven decision-making processes.

    Additionally, the dashboard enables stakeholders to identify potential marketing opportunities, optimize resource allocation, and enhance urban planning strategies by leveraging insights gained from the visualization of POIs and traffic hotspots.
    """)
    
    st.write("## Key Features")
    st.markdown("""
    The dataset comprises two main components: **traffic hotspots** and **points of interest (POIs)**. 
    """)

    # Detailed description for traffic hotspots
    st.markdown("""
    **Traffic Hotspots:**
    - **Format:** GeoJSON file
    - **Size:** More than 200 entries
    - **Attributes:** Each entry includes longitude and latitude coordinates along with the level of traffic, ranging from 0 to 5.
    - **Description:** The dataset provides information about traffic congestion hotspots within the area of interest. Each entry represents a specific location where traffic congestion is observed, with the level of congestion categorized on a scale of 0 to 5.
    """)
    if st.checkbox("***Show Traffic Data***"):
        st.write(traffic[:10])

    # Detailed description for points of interest (POIs)
    st.markdown("""
    **Points of Interest (POIs):**
    - **Format:** Multiple files including SHP, PRJ, DBF, and SHX
    - **Attributes:** Each POI entry includes longitude and latitude coordinates along with its type, such as education, shop, etc.
    - **Description:** The POIs dataset contains information about various points of interest scattered throughout the area. Each POI represents a specific type of amenity, service, or attraction, such as educational institutions, shops, restaurants, etc. The dataset allows for the exploration of the spatial distribution of different types of POIs within the region of interest.
    """)
            
    if st.checkbox("***Show POIs Data***"):
        st.write(pois[:10])
        
        
def show_hotspots():
    # In this function will be be discussing the distribution and other insights from hotspots data
    st.markdown("## Traffic Hotspots")
    st.info("A traffic hotspot is a location on a road network that experiences frequent and significant congestion. These areas are known for delays and slowdowns in traffic flow.")
     
    col1,col2 = st.columns([0.6,0.6])
    
    with col1:
        st.markdown("### Bar Chart")
        # Get the counts for each level
        counts = traffic['level'].value_counts().reset_index()
        counts.columns = ['level', 'count']
        fig = px.bar(counts, x='level', y='count', color='level',color_continuous_scale="Jet", labels={'level': 'Traffic Level', 'count': 'Count'}, title='Distribution of Traffic Levels')
        st.plotly_chart(fig, config={'displayModeBar': False})
        # now we will do a bit of customization to chart. like having different color for each level
        
    with col2:
        st.markdown("### Donut Chart")
        piechart = px.pie(traffic, names='level', hole=0.3, title='Distribution of Traffic Levels')
        st.plotly_chart(piechart, config={'displayModeBar': False})
        
    st.markdown("## Traffic Hotspots Map")
    col1, col2 = st.columns([0.4, 0.6])
    slider_value = 0
    with col1:
        slider_value = st.slider(max_value=5, min_value=0, label="Select Traffic Level", key="level")
        # Filter the data based on the selected level
        filtered_data = traffic[traffic['level'] == slider_value]
    
    if slider_value == 0:
        # I will be ploting plotly map here, since provide a better and easy customization for map
        fig = px.scatter_mapbox(traffic, lat="latitude", lon="longitude", color="level", color_continuous_scale="Jet",zoom=10, mapbox_style="open-street-map", height=650)
        st.plotly_chart(fig, use_container_width=True, config = {'displayModeBar': False})
    else:
        st.map(filtered_data)
    
    heatmap_data = traffic.groupby(['latitude', 'longitude'])['level'].mean()
    heatmap_data = heatmap_data.reset_index(name='intensity')

    # Create the heatmap using Plotly Express density_mapbox
    fig = px.density_mapbox(heatmap_data, lat='latitude', lon='longitude', z='intensity', radius=10, zoom=10, mapbox_style="open-street-map", height=650, color_continuous_scale="Jet", title='Heatmap of Points of Interest (POIs)')  
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False}) 
    

def show_pois():
    # here we are also going to show the distribution of POIs and then map
    st.markdown("## Points of Interest (POIs)")
    st.info("Points of Interest (POIs) are specific locations that are of interest to individuals or communities. These locations may include educational institutions, healthcare facilities, shopping centers, etc.")
    col1,col2 = st.columns([0.6,0.6])
    
    with col1:
        st.markdown("### Bar Chart")
        # Get the counts for each level
        counts = pois['type'].value_counts().reset_index()
        counts.columns = ['type', 'count']
        fig = px.bar(counts, x='type', y='count', color='type',color_continuous_scale="Jet", labels={'Type': 'POI Name', 'count': 'Count'}, title='Distribution of POIs')
        st.plotly_chart(fig, config={'displayModeBar': False})
        # now we will do a bit of customization to chart. like having different color for each level
        
    with col2:
        st.markdown("### Donut Chart")
        # here we will be using plotly to draw donut chart
        piechart = px.pie(pois, names='type', hole=0.3, title='Distribution of POIs')
        st.plotly_chart(piechart, config={'displayModeBar': False})
        
    st.markdown("## POIS Map")
    col1, col2 = st.columns([0.4, 0.6])
    
    pois_types = pois['type'].unique()
    pois_types = list(pois_types)
    pois_types.insert(0, "All")
    with col1:
        # here we will use dropdown menu 
        category = st.selectbox("Select POI Type",pois_types)
        # Filter the data based on the selected level
        filtered_data = pois[pois['type'] == category]
    
    if category == "All":
        # I will be ploting plotly map here, since provide a better and easy customization for map
        fig = px.scatter_mapbox(pois, lat="latitude", lon="longitude", color="type",zoom=10, mapbox_style="open-street-map", height=650)
        st.plotly_chart(fig, use_container_width=True, config = {'displayModeBar': False})
    else:
        st.map(filtered_data)
        

    if category == "All":
        # Count the occurrences of each place
        heatmap_data = pois.groupby(['latitude', 'longitude'])['type'].value_counts().reset_index(name='count')
    else:
        heatmap_data = filtered_data.groupby(['latitude', 'longitude'])['type'].value_counts().reset_index(name='count')

    # Create the heatmap using Plotly Express density_mapbox
    fig = px.density_mapbox(heatmap_data, lat='latitude', lon='longitude', z='count', radius=10, zoom=10, mapbox_style="open-street-map", height=650, color_continuous_midpoint=heatmap_data['count'].mean(), color_continuous_scale="Jet", title='Heatmap of Points of Interest (POIs)')

    # Display the heatmap
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        
def show_relation_bw_hotspots_pois():
    st.markdown("## Relationship Between Traffic Hotspots and Points of Interest (POIs)")
    
    st.markdown("### Heatmap Regarding Hostsopts Having Most POIS in Near Point (0.01)")
    
    radius = 0.01  # Adjust this value based on your data and requirements

    poi_counts = {}

    for hotspot_index, hotspot in traffic.iterrows():
        distances = np.sqrt((pois['latitude'] - hotspot['latitude'])**2 + (pois['longitude'] - hotspot['longitude'])**2)
        
        near_pois = pois[distances <= radius]
        poi_type_counts = near_pois['type'].value_counts()
        
        if not poi_type_counts.empty:
            most_prevalent_poi_type = poi_type_counts.idxmax()
            poi_counts[hotspot_index] = {'poi_count': len(near_pois), 'most_prevalent_poi_type': most_prevalent_poi_type}
        else:
            poi_counts[hotspot_index] = {'poi_count': 0, 'most_prevalent_poi_type': None}

    counts_df = pd.DataFrame.from_dict(poi_counts, orient='index').reset_index()
    counts_df = counts_df.rename(columns={'index': 'hotspot_index'})

    hotspots_with_counts = traffic.merge(counts_df, left_index=True, right_on='hotspot_index', how='left')

    # Plot the scatter map with hover information
    fig = px.scatter_mapbox(hotspots_with_counts, lat='latitude', lon='longitude',
                            size='poi_count', color='poi_count', hover_name='most_prevalent_poi_type',
                            color_continuous_scale="Jet", size_max=30, zoom=10, 
                            mapbox_style="open-street-map", height=650)
    st.plotly_chart(fig, use_container_width=True)

    
    st.subheader("Dual-layer Map: Traffic Hotspots and Heatmap of POIs")
    fig = px.scatter_mapbox(traffic, lat="latitude", lon="longitude",color="level",size="level",
                            color_continuous_scale="Jet", zoom=10,
                            mapbox_style="open-street-map", height=650)

    # Add density map layer with color scale
    heatmap = px.density_mapbox(pois, lat='latitude', lon='longitude', z=None,
                                radius=10, color_continuous_scale="Jet",
                                mapbox_style="open-street-map", zoom=10)

    fig.add_trace(heatmap.data[0])
    st.plotly_chart(fig, use_container_width=True,  config={'displayModeBar': False})
    
def show_about_me():
    st.markdown(""" ## About Me

    Hello! I'm a Computer Science student with a keen interest in Data Science and Android Development. My journey has been driven by a passion for understanding the complexities of data and how it can be harnessed to build innovative solutions. Recently, I've embarked on an exciting path towards mastering Generative AI, exploring how these cutting-edge technologies can transform the digital landscape.

    ### Explore My Writing

    I regularly share insights and detailed write-ups about my projects and learning experiences on Medium. Check out my [Medium blog](https://medium.com/@m.muneeb.ur.rehman.2000) to get a deeper understanding of my work and thoughts in the realm of tech. 

    ### Connect With Me

    Curious about my projects? Let’s connect! You can follow my journey and updates on my work:
    - **GitHub**: [Visit my GitHub profile](https://github.com/Muneeb1030) for a dive into my coding adventures and projects.
    - **LinkedIn**: [Connect with me on LinkedIn](https://www.linkedin.com/in/muhammad-muneeb-ur-rehman-75482527a/) where I share insights, progress, and connect with fellow tech enthusiasts.

    I'm always open to collaborating on projects and innovative ideas in the realms of Data Science and AI!
    """)
        
        
def main():
    st.set_page_config(page_title="Urban Insights: Exploring Traffic Hotspots and Points of Interest", page_icon=":car:", layout="wide", initial_sidebar_state="collapsed")
    st.title("Urban Insights: Exploring Traffic Hotspots and Points of Interest")
    Show_Home_Page()
    show_hotspots()
    show_pois()
    show_relation_bw_hotspots_pois()
    show_about_me()
    
if __name__ == '__main__':
    # DatabaseInsertion()
    pois, traffic = DatabaseRetrieval()
    main()
    
    

