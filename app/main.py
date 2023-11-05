from fastapi import FastAPI
import datetime

from app.api_clients.cds import get_historical_wind_data
from app.utils.wind_data_transform import create_wind_geojson
from app.models import BoundingBox, WindParameterValue

app = FastAPI()


@app.post("/api/wind/")
def get_wind_data(parameter: WindParameterValue, bb: BoundingBox):

    # Specify paths
    # TODO create path dynamically, based on project ID
    path_to_wind_data_nc = "data/intermediate_wind_data.nc"

    # Download data from CDS for last 5 years from today
    today = datetime.date.today()
    years = [str(today.year - i) for i in range(1, 10)]
    bb_list = [bb.min_lat, bb.min_lon, bb.max_lat, bb.max_lon]
    get_historical_wind_data(path_to_wind_data_nc, bb_list, years)

    # Transform wind data to aggregated direction or speed and save as geojson
    wind_data = create_wind_geojson(
        path_to_wind_data_nc, parameter, years)

    return wind_data
