# Data Broker of Permacultr project

The data broker accesses various APIs, transforms the data and exposes the transformed data via API

## Set-UP

- Create a .env file in the project root directory
- Here you can store all API keys and other credentials
- For using the CDS API set **CDS_API_URL** and **CDS_API_KEY**

## TODOs

- Update readme
- Implement agroclimatic indicators
  - Predownload of data
  - Mapping from parameter to data path
  - BEDD file seems to big to load. Slim it down
- Implement tests, which can be run each time I make changes

## Backlog

- How to save intermediate data?
  - There might be more users downloading data at the same time
- Integration of GraphCast weather forecasting into service
