# Data Broker of Permacultr project

The data broker accesses various APIs, transforms the data and exposes the transformed data via API

## Set-UP

- Create a .env file in the project root directory+
- Here you can store all API keys and other credentials
- For using the CDS API set **CDS_API_URL** and **CDS_API_KEY**

## TODOs

- It can happen that the API freezes when the bb box is too big
  - Implement Error saying that request is too big
  - Set maximum bounding box size
  - Try out streaming json (https://www.vidavolta.io/streaming-with-fastapi/)
- Update readme
- Implement tests, which can be run each time I make changes

## Backlog

- Integration of GraphCast weather forecasting into service
