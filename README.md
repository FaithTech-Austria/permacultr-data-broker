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

## Sun

## Elevation

## Next steps

- Write function for processing netcdf file.
  - Calculate monthly aggregated wind speed and wind direction from u and v component (x)
  - Refactor code
  - Integrate wind into API
