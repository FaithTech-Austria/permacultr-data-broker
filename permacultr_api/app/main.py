from fastapi import FastAPI
import datetime
import geojson
from dotenv import load_dotenv
import os
import time

from app.api_clients.cds import get_historical_wind_data
from app.api_clients.osmnx import get_data_from_osmnx
from app.api_clients.open_elevation import get_elevation_data
from app.utils.wind_data_transform import create_wind_geojson
from app.utils.elevation_data_transform import (
    extract_elevation_data,
    create_regular_grid,
    create_elevation_raster,
    create_contour_lines_geojson)
from app.models import BoundingBox, WindParameterValue, ContourInterval, Resolution, NetworkTypeValue

load_dotenv("/code/.env")

# Load paths from env variables
PATH_TO_HISTORIC_WIND_DATA = os.getenv("PATH_TO_HISTORIC_WIND_DATA")
PATH_TO_ELEVATION_RASTER = os.getenv("PATH_TO_ELEVATION_RASTER")
PATH_TO_CONTOUR_LINES = os.getenv("PATH_TO_CONTOUR_LINES")

app = FastAPI()


@app.post("/api/wind/")
def get_wind_data(bb: BoundingBox, parameter: WindParameterValue) -> dict:
    """get monthly wind speed and direction averaged over last 10 years """

    # Download data from CDS for last 10 years from today
    today = datetime.date.today()
    years = [str(today.year - i) for i in range(1, 10)]
    get_historical_wind_data(PATH_TO_HISTORIC_WIND_DATA, bb, years)
    wind_data = create_wind_geojson(
        PATH_TO_HISTORIC_WIND_DATA, parameter, years)

    return wind_data


@app.post("/api/contour_lines/")
def get_contour_lines(contour_interval: ContourInterval, bb: BoundingBox, resolution: Resolution) -> dict:
    """get contour lines within bounding box, interpolated to contour interval. """

    # create longitude and latitude array representing a regular grid
    longitude_arr, latitude_arr = create_regular_grid(
        bb, resolution.value)

    # create list with coordinate tuples
    grid_points = [(lat, lon) for lat, lon in zip(
        latitude_arr.flatten(), longitude_arr.flatten())]

    # send no more than 100 location requests to the API
    elevation_data_ls = []
    chunk_size = 100
    for i in range(0, len(grid_points), chunk_size):
        chunk = grid_points[i:i + chunk_size]
        # time.sleep(2)
        elevation_data_chunk = get_elevation_data(chunk)
        elevation_data_ls.append(elevation_data_chunk)

    elevation_data = {"results": []}
    for elev_data_chunk in elevation_data_ls:
        elevation_data["results"] += elev_data_chunk["results"]

    elevation_data_dict = extract_elevation_data(elevation_data)

    create_elevation_raster(longitude_arr, latitude_arr,
                            elevation_data_dict, PATH_TO_ELEVATION_RASTER)

    # create contour lines
    create_contour_lines_geojson(PATH_TO_ELEVATION_RASTER,
                                 PATH_TO_CONTOUR_LINES, contour_interval.value)

    # read geojson from file and return
    with open(PATH_TO_CONTOUR_LINES) as f:
        contour_lines = geojson.load(f)

    return contour_lines


@app.post("/api/osm/buildings/")
def get_buildings_from_osm(bb: BoundingBox) -> dict:
    """get osm buildings from osmnx api"""
    buildings = get_data_from_osmnx(bb, "buildings")
    return buildings


@app.post("/api/osm/streets/")
def get_buildings_from_osm(bb: BoundingBox, network_type: NetworkTypeValue) -> dict:
    """get osm streets from osmnx api"""
    streets = get_data_from_osmnx(bb, "streets", network_type.value)
    return streets


@app.post("/api/osm/waterways/")
def get_buildings_from_osm(bb: BoundingBox) -> dict:
    """get osm waterways from osmnx api"""
    waterways = get_data_from_osmnx(bb, "waterways")
    return waterways
