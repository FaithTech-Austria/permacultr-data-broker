from fastapi import FastAPI, Query
from pydantic import BaseModel
from api_clients.cds import get_historical_wind_data
from utils.data_transform import create_wind_geojson
from enum import Enum
import datetime
from typing import List

"""
{
  "min_lat": 48.289416,
  "min_lon": 14.263430,
  "max_lat": 48.315876,
  "max_lon": 14.314499
}
"""

# TODO instead of Bounding, mabye just a coordinate would be better-


class BoundingBox(BaseModel):
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float


class WindParameterValue(str, Enum):
    speed = "speed"
    direction = "direction"


app = FastAPI()


@app.post("/wind")
def get_wind_data(parameter: WindParameterValue, bb: BoundingBox):

    # Specify paths
    # TODO create path dynamically, based on project ID
    path_to_wind_data_nc = "../data/intermediate_wind_data.nc"

    # Download data from CDS for last 5 years from today
    today = datetime.date.today()
    years = [str(today.year - i) for i in range(1, 10)]
    bb_list = [bb.min_lat, bb.min_lon, bb.max_lat, bb.max_lon]
    get_historical_wind_data(path_to_wind_data_nc, bb_list, years)

    # Transform wind data to aggregated direction or speed and save as geojson
    wind_data = create_wind_geojson(
        path_to_wind_data_nc, parameter, years)

    return wind_data
