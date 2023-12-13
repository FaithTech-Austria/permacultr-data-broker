# Data Broker of Permacultr project

The data broker accesses various APIs, transforms the data and exposes the transformed data via API

## Set-Up

- Create a .env file in the project root directory
- Here you can store all API keys and other credentials
- For using the CDS API set **CDS_API_URL** and **CDS_API_KEY**

## Start service

Start FastAPI by running the following command in the terminal

```
docker compose up
```

After that, you can check out the API at
http://localhost:8080/docs

## Integrated data

### 1. Get OSM Buildings

**Endpoint:** `/api/osm/buildings/`  
**Method:** `POST`  
**Parameters:**

- `bb` (_BoundingBox_): Bounding box coordinates to define the area of interest.

**Description:**  
Retrieve OpenStreetMap (OSM) building data within the specified bounding box.

### 2. Get OSM Streets

**Endpoint:** `/api/osm/streets/`  
**Method:** `POST`  
**Parameters:**

- `bb` (_BoundingBox_): Bounding box coordinates to define the area of interest.
- `network_type` (_NetworkTypeValue_): Type of street network (e.g., 'all', 'walk').

**Description:**  
Retrieve OSM street data within the specified bounding box, considering the specified network type.

### 3. Get OSM Waterways

**Endpoint:** `/api/osm/waterways/`  
**Method:** `POST`  
**Parameters:**

- `bb` (_BoundingBox_): Bounding box coordinates to define the area of interest.

**Description:**  
Retrieve OSM waterway data within the specified bounding box.

### 4. Get Historic Wind Data

**Endpoint:** `/api/wind/`  
**Method:** `POST`  
**Parameters:**

- `bb` (_BoundingBox_): Bounding box coordinates to define the area of interest.
- `parameter` (_WindParameterValue_): Wind parameter (e.g., 'wind_speed', 'wind_direction').

**Description:**  
Retrieve monthly wind speed and direction averaged over the last 10 years within the specified bounding box.

### 5. Get Contour Lines

**Endpoint:** `/api/contour_lines/`  
**Method:** `POST`  
**Parameters:**

- `contour_interval` (_ContourInterval_): Contour interval for elevation data.
- `bb` (_BoundingBox_): Bounding box coordinates to define the area of interest.
- `resolution` (_Resolution_): Spatial resolution of the grid.

**Description:**  
Generate contour lines based on elevation data within the specified bounding box and resolution.

**Note:**
For retrieving Elevation data for contour lines, two data sources are available.

1. Usage of hosted opentopodata API (https://www.opentopodata.org/). Elvation points globally available, but limited requests.
2. Self-hosted elevation API. For running this API elevation tiles have to be stored in project folder.

You can easily switching from the one option to the other by (un-)commenting the following lines in the **main.py** file

```python
# from app.api_clients.open_elevation import get_elevation_data
from app.api_clients.opentopodata import get_elevation_data
```

### 6. Get Agroclimatic Indicators (Still under development)

**Endpoint:** `/api/agroclimatic_indicators/`  
**Method:** `POST`  
**Parameters:**

- `bb` (_BoundingBox_): Bounding box coordinates to define the area of interest.
- `parameter` (_AgroclimaticIndicator_): Agroclimatic indicator (e.g., 'biologically_effective_degree_days').

**Description:**  
Retrieve agroclimatic indicators for the period 1981-2010 within the specified bounding box.
