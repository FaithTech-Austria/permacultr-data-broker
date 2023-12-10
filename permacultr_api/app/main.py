from fastapi import FastAPI
import datetime
import geojson
from dotenv import load_dotenv
import os

from app.api_clients.cds import download_wind_data_from_cds, download_agroclimatic_indicators_from_cds
from app.api_clients.osmnx import get_data_from_osmnx
from app.api_clients.open_elevation import get_elevation_data
from app.utils.utils import validate_bounding_box_size
from app.utils.wind_data_transform import create_wind_geojson
from app.utils.agroclimatic_indicators_transform import create_agroclimatic_indicators_json
from app.utils.elevation_data_transform import (
    extract_elevation_data,
    create_regular_grid,
    create_elevation_raster,
    create_contour_lines_geojson)
from app.models import (BoundingBox, WindParameterValue, ContourInterval,
                        Resolution, NetworkTypeValue, AgroclimaticIndicator)


# mapping between agroclimatic indicator to path where data is stored
PATH_TO_AC_DATA = {
    "biologically_effective_degree_days": "PATH_TO_BEDD"
}


load_dotenv()

# Load paths from env variables
PATH_TO_HISTORIC_WIND_DATA = os.getenv("PATH_TO_HISTORIC_WIND_DATA")
PATH_TO_ELEVATION_RASTER = os.getenv("PATH_TO_ELEVATION_RASTER")
PATH_TO_CONTOUR_LINES = os.getenv("PATH_TO_CONTOUR_LINES")

app = FastAPI()


@app.post("/api/osm/buildings/", tags=["Base Map"])
def get_buildings_from_osm(bb: BoundingBox) -> dict:
    """get osm buildings from osmnx api"""
    validate_bounding_box_size(bb, 1)
    buildings = get_data_from_osmnx(bb, "buildings")
    return buildings


@app.post("/api/osm/streets/", tags=["Base Map"])
def get_streets_from_osm(bb: BoundingBox, network_type: NetworkTypeValue) -> dict:
    """get osm streets from osmnx api"""
    streets = get_data_from_osmnx(bb, "streets", network_type.value)
    return streets


@app.post("/api/osm/waterways/", tags=["Base Map"])
def get_waterways_from_osm(bb: BoundingBox) -> dict:
    """get osm waterways from osmnx api"""
    waterways = get_data_from_osmnx(bb, "waterways")
    return waterways


@app.post("/api/wind/", tags=["Sector Map"])
def get_wind_data(bb: BoundingBox, parameter: WindParameterValue) -> dict:
    """get monthly wind speed and direction averaged over last 10 years """

    # Download data from CDS for last 10 years from today
    today = datetime.date.today()
    years = [str(today.year - i) for i in range(1, 10)]
    download_wind_data_from_cds(PATH_TO_HISTORIC_WIND_DATA, bb, years)
    wind_data = create_wind_geojson(
        PATH_TO_HISTORIC_WIND_DATA, parameter, years)

    return wind_data


@app.post("/api/contour_lines/", tags=["Sector Map"])
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


@app.post("/api/agroclimatic_indicators/", tags=["Climatic Info"])
def get_agroclimatic_indicators_data(bb: BoundingBox, parameter: AgroclimaticIndicator) -> dict:
    """get agroclimatic indicators for period 1981 - 2010"""

    # download_agroclimatic_indicators_from_cds(
    #    PATH_TO_AGROCLIMATIC_INDICATORS, parameter.value)
    # create dict of data at specific location

    path_to_data = PATH_TO_AC_DATA[parameter]
    path_to_nc_file = os.getenv(path_to_data)

    agroclimatic_indicator_dict = create_agroclimatic_indicators_json(
        path_to_nc_file, bb, parameter)
    # return agroclimatic_indicator_dict

    return agroclimatic_indicator_dict
