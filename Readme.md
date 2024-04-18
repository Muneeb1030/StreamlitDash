# Traffic Hotspots and Point of Interests of Lahore Dashboard Using Streamlit
In this Assignment, i will be creating a dashbpard for the provided dataset of Traffic Hotspots and POIs of Lahore by my Professor using streamlit. This assigment has multiple datasets and tools to create dashboard with. In this will only be discussing Streamlit and The Provided Dataset to extract insights for useful purposes.

## Tools Utilized
- StreamLit for DashBoard UI (it is basically a library but i have put it under this Heading)
- Postgres Database to Save the Data.
- ChatGPT to Generate Code and Help when needed.

## Langauge
I will be using Python 3.12 for this assignment

## Steps before starting the actual dashbaord
### Step 1:- Creating Git 
- Run the following command to create git locally later i will be publishing this project to my github.
 ```
 git init
 ```
- Create gitignore file to avoid tracking the dataset files. (The dataset is private used in one of my professor research. so i can not provide it)

### Step 2:- Dataset Nature Discussed
The dataset is geo spatial in nature and There are two types of file provided. 
- First one is hotspots which is ```geojson``` in format
- Second is POIs which has three files named ```.prj, .shp and shx```. The ```dbf``` is not a standard in geo spatial datset and when i discussed it earlier with Chatgpt it said it depends upon the nuture of dataset and it collection method to have some specific files.
### Hotspots
- **Format:** GeoJSON file
- **Size:** More than 200 entries
- **Attributes:** Each entry includes longitude and latitude coordinates along with the level of traffic, ranging from 0 to 5.
- **Description:** The dataset provides information about traffic congestion hotspots within the area of interest. Each entry represents a specific location where traffic congestion is observed, with the level of congestion categorized on a scale of 0 to 5.
### POIs
- **Format:** Multiple files including SHP, PRJ, DBF, and SHX
- **Attributes:** Each POI entry includes longitude and latitude coordinates along with its type, such as education, shop, etc.
- **Description:** The POIs dataset contains information about various points of interest scattered throughout the area. Each POI represents a specific type of amenity, service, or attraction, such as educational institutions, shops, restaurants, etc. The dataset allows for the exploration of the spatial distribution of different types of POIs within the region of interest.

### Step 3:- Create a Virtual Environment for the project
- Run the following command in command prompt and (venv) will appear in begining of Path, meaning virtual environment is activated.
```
python -m venv name 
```
The convention is to use venv as name.
If you are using git DO ADD VENV folder in gitignore to avaiod excessive tracking
- Now run the following command to activate the virtual environment
```
venv\Scripts\activate.bat
```

### Step 4:- Installing Libraries required
We need the following libraries for it to work 
- Pandas
- GeoPandas
- Psycopg2 (this is for postgres connection in python script)
- Streamlit
- Plotly (Some graphs like heat maps are very basic in Streamlit)

I will be providing requirement.txt file in order to avaoid installing each library/package individually
To check whether Streamlit is installed we can use ```streamlit hello```. it will launch a localhost.
### step 5:- Load Data in the script
- First Create a ```.py``` file.
- Import the required Libraries
```
Here I want to mention that i have already submitted the assignment and now i am just recording it for my youtube channel, so i have encountered and overcame all the issues in the data set. so i will only provide the overview of the script i have written to read and put the data in the database.
```
**Note:** The thing with Geo Spatial data is that on the Earth surface, a location is specified by its longitude and latitude and the range of longitude and latitude is [-180, 180]. But the number in geometery columns are not nearky remsembling the co-ordinates. this is becuase when geo spatial data is collected thorugh a certain sensor, it basically projects it on a 2d plane rather than a sphere, hence no degrees for measurement. To make this data usable we will need to look into the ```.prj``` file and get the projection data from it.

- Create a Database and Then run the DatabaseInsertion function. Make sure to Correct the Data Paths.
    - The function will create Necessary tables in the Database
    - Read the data from the files.
    - Convert the Geometry to required projection
    - Insert the Data into Database

- Now retrieve the data from database using the DatabaseRetrival Function. this function will get the data from database put it in Dataframes and return them.

- Before Discussing the Dashboard lets discuss a little bit of syntax provided by streamlit
    - Always make sure to check ```Always Rerun``` Option.
    - I will demonstrate some of the syntax of streamlit, which is ostly used in this dashbaord.

### Streamlit Tutorial
```
# st.title("Home Page")
# st.header("Welcome to the Home Page")
st.title("Home Page")
st.header("Welcome to the Home Page")
st.subheader("This is a subheader")

st.markdown("***This*** *is* a **markdown** text")
'''
# * means italic
# ** means bold
# *** means bold and italic
'''

st.write("This is a **write** function") 

st.info("This is an info message")
st.success("This is a success message") 
st.warning("This is a warning message") 
st.error("This is an error message") 
st.bar_chart(pois['type'].value_counts(),color='#ff0000') 
st.divider()
val = st.checkbox("This is a checkbox") 

if val:
    st.write("Checkbox is checked")
    
value  = st.slider("This is a slider", min_value=0, max_value=100) 
st.write(f"Slider value is {value}")
st.plotly_chart(px.bar(pois['type'].value_counts()))
st.balloons()

st.write("This is a table") 
st.table(pois[:10])

st.sidebar.title("This is a sidebar")
st.sidebar.file_uploader("This is a file uploader")
opt = st.sidebar.selectbox("This is a selectbox", ["Option 1", "Option 2", "Option 3"]) 
st.sidebar.write(f"Selected option is {opt}")

col1, col2  = st.columns([0.5,2]) # Create 2 columns

with col1:
    st.write("This is column 1")

with col2:
    st.write("This is column 2")
```