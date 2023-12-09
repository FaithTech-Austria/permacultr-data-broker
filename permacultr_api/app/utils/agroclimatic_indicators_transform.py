import netCDF4 as nc
import numpy as np
import datetime


def get_nc_data_at_location(site_lat: float, site_lon: float, lat: np.array, lon: np.array, var: np.array) -> np.array:
    """get data of nc grid cell at specific location"""

    lat_idx = (np.abs(lat-site_lat)).argmin()
    lon_idx = (np.abs(lon-site_lon)).argmin()
    return var[:, lat_idx, lon_idx]


def create_agroclimatic_indicators_json(path_to_nc_file: str, bounding_box: dict, parameter: str) -> dict:
    """Create dict for agroclimatic indicator data containing date and value for a specific parameter at the location of the bounding box."""

    with nc.Dataset(path_to_nc_file, "r") as f:
        lat = f.variables['lat'][:]
        lon = f.variables['lon'][:]
        time = f.variables['time'][:]
        var = f.variables[parameter][:]

    values = get_nc_data_at_location(
        bounding_box.max_lat, bounding_box.max_lon, lat, lon, var)

    data_json = {parameter: []}
    date_base = datetime.datetime.strptime("01-01-1860", "%d-%m-%Y")

    for days_since_1860, value in zip(time, values):
        date = date_base + datetime.timedelta(days=days_since_1860)
        data_json[parameter].append(
            {"date": date, "value": value})

    return data_json
