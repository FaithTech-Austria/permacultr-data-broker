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

The API can be accessed in the following way:

```bash
curl -X 'POST' \
  'http://localhost:8080/api/elevation/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contour_interval": {
    "value": 10
  },
  "bb": {
    "min_lat": -8.907363,
    "min_lon": 33.423929,
    "max_lat": -8.899648,
    "max_lon": 33.435409
  },
  "resolution": {
    "value": 30
  }
}
'
```

## Sun

## TODOs

- Set maximum bounding box size (e.g. 1km2 == 100 hacters)
- Update readme
- Integrate OSM API to retrieve buildings, streets ...
- Implement tests, which can be run each time I make changes

- Current state:
  - API is freezing when I try to get buildings. Probably the response data is to much. Try to slim it down
  - There might be issues with the volumes. It seemed that code is not automatically updated.
