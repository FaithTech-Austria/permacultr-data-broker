# Data Broker of Permacultr project

The data broker accesses various APIs, transforms the data and exposes the transformed data via API

## Set-UP

- Create a .env file in the project root directory+
- Here you can store all API keys and other credentials
- For using the CDS API set **CDS_API_URL** and **CDS_API_KEY**

### Conda installs

```bash
conda install -c conda-forge gdal
pip install -r requirements.txt
```

## Wind

Wind speed and direction patterns are required.
Therefore we want to download wind data for the last X year of the AOI and calculate monthly averages over the years.
There are some API providers for wind data, but it seems that for historical wind data you have to pay.
Therefore we are utilizing the ERA5 data from the Climate data store.

Example for request to FastAPI for wind data

```bash
curl -X 'POST' \
  'http://localhost:8000/wind?parameter=direction' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "min_lat": 48.289416,
  "min_lon": 14.263430,
  "max_lat": 48.315876,
  "max_lon": 14.314499
}'
```

## Elevation

We are using open-elevation to host an Elevation API.

For setting up the API the following steps are taken:

1. Download SRTM elevation data for Tanzania (30m resolution) from https://opendata.rcmrd.org/datasets/tanzania-srtm-dem-30-meters

2. Create a new directory /data where the DEM will be stored.

3. Tile the data into 100 tiles

```bash
docker run -it -v /data:/code/data openelevation/open-elevation /code/create-tiles.sh  /code/data/Tanzania_SRTM30meters.tif 10 10
```

4. Remove the DEM from the folder. Only the tiles should remain there.

5. Run the server

```bash
docker run -it -v /data:/code/data -p 80:8080 openelevation/open-elevation
```

6. Now you can pose queries to the API

```bash
curl 'http://localhost:8000/api/v1/lookup?locations=-4.7,30'
```

### Next steps:

- We want to create contourlines within the bounding box and return a Geojson containing the contour lines
- Making elevation contour lines available in our API

- Contour Lines:
  - Access SRTM 30 data from somewhere
  - Clip it to bounding box and save it
  - with gdal, create contour lines and save as geojson

## Sun

### TODOs

- Set up of docker, with volume bind to code and enabling update in docker when code is changed
- Create environment, where gdal works with other packages. Create requirements file with versions
