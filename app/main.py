from fastapi import FastAPI
import datetime
import geojson
from dotenv import load_dotenv, find_dotenv, dotenv_values
import os

from app.api_clients.cds import get_historical_wind_data
from app.api_clients.opentopodata import get_elevation_data
from app.utils.wind_data_transform import create_wind_geojson
from app.utils.elevation_data_transform import (
    extract_elevation_data,
    create_regular_grid,
    create_elevation_points_geojson,
    create_elevation_raster,
    create_contour_lines_geojson)
from app.models import BoundingBox, WindParameterValue, ContourInterval

find_dotenv("/code/.env")

# Load paths from env variables
PATH_TO_HISTORIC_WIND_DATA = os.getenv("PATH_TO_HISTORIC_WIND_DATA")
PATH_TO_ELEVATION_RASTER = os.getenv("PATH_TO_ELEVATION_RASTER")
PATH_TO_ELEVATION_POINTS = os.getenv("PATH_TO_ELEVATION_POINTS")
PATH_TO_CONTOUR_LINES = os.getenv("PATH_TO_CONTOUR_LINES")


app = FastAPI()


@app.post("/api/wind/")
def get_wind_data(parameter: WindParameterValue, bb: BoundingBox) -> dict:

    # Download data from CDS for last 5 years from today
    today = datetime.date.today()
    # TODO integrate into API --> average from last x years
    years = [str(today.year - i) for i in range(1, 10)]
    bb_list = [bb.min_lat, bb.min_lon, bb.max_lat, bb.max_lon]
    get_historical_wind_data(PATH_TO_HISTORIC_WIND_DATA, bb_list, years)

    # Transform wind data to aggregated direction or speed and save as geojson
    wind_data = create_wind_geojson(
        PATH_TO_HISTORIC_WIND_DATA, parameter, years)

    return wind_data


@app.post("/api/elevation/")
def get_contour_lines(contour_interval: ContourInterval, bb: BoundingBox) -> dict:

    # TODO solver this more elegantly.
    # spacing should always be 30 if srtm30 is used.
    spacing = 500

    print(f"Path to elevation: {PATH_TO_ELEVATION_POINTS}")

    # create longitude and latitude array representing a regular grid
    bb_list = [bb.min_lat, bb.min_lon, bb.max_lat, bb.max_lon]
    longitude_arr, latitude_arr = create_regular_grid(
        bb_list, spacing)

    # create list with coordinate tuples
    grid_points = [(lat, lon) for lat, lon in zip(
        latitude_arr.flatten(), longitude_arr.flatten())]

    # get elevation data
    elevation_data = get_elevation_data(grid_points)

    # TODO pack everything below into function and outsource to elevation_data_transform
    elevation_data_dict = extract_elevation_data(elevation_data)

    create_elevation_points_geojson(
        elevation_data_dict, PATH_TO_ELEVATION_POINTS)

    create_elevation_raster(longitude_arr, latitude_arr,
                            elevation_data_dict, PATH_TO_ELEVATION_RASTER)

    # create contour lines
    create_contour_lines_geojson(PATH_TO_ELEVATION_RASTER,
                                 PATH_TO_CONTOUR_LINES, contour_interval.value)

    # read geojson from file and return
    with open(PATH_TO_CONTOUR_LINES) as f:
        contour_lines = geojson.load(f)

    return contour_lines
