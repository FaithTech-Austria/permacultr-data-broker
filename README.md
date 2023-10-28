# Data Broker of Permacultr project

The data broker accesses various APIs, transforms the data and exposes the transformed data via API

## Set-UP

- Create a .env file in the project root directory+
- Here you can store all API keys and other credentials
- For using the CDS API set **CDS_API_URL** and **CDS_API_KEY**

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

## Sun

## Elevation

## Next steps

- Write function for processing netcdf file.
  - Qualitative validation of wind data by using some example areas and check wind patterns
