import netCDF4 as nc
import numpy as np
from geojson import Feature, Point, FeatureCollection, dump
import os


def read_nc_variables(nc_file):
    u10 = nc_file.variables["u10"][:]
    v10 = nc_file.variables["v10"][:]
    return u10, v10


def calculate_wind_properties(u10, v10):
    wind_speed = np.sqrt(u10**2 + v10**2)
    wind_direction = (np.arctan2(v10, u10) * 180 / np.pi) % 360
    return wind_speed, wind_direction


def calculate_monthly_averages(data, nr_years):
    return data.reshape(nr_years, 12, data.shape[1], data.shape[2]).mean(axis=0)


def create_geojson_features(latitude, longitude, data, months, data_type):
    features = []
    for i, lat in enumerate(latitude):
        for j, lon in enumerate(longitude):
            geom = Point((float(lon), float(lat)))
            data_point = data[:, i, j]
            if not np.ma.is_masked(data_point[0]):
                data_point_dict = {month: data_point[i]
                                   for i, month in enumerate(months)}
                feature = Feature(geometry=geom, properties=data_point_dict)
                features.append(feature)
    return FeatureCollection(features)


def transform_wind_nc_to_geojson(path_to_wind_nc_file: str, path_to_wind_speed: str, path_to_wind_direction: str):

    # Read nc file netcdf
    nc_file = nc.Dataset(path_to_wind_nc_file)

    try:
        u10, v10 = read_nc_variables(nc_file)

        # Calculate wind speed and direction
        wind_speed, wind_direction = calculate_wind_properties(u10, v10)

        # Calculate monthly average of wind speed and direction
        nr_years = int(wind_speed.shape[0] / 12)
        wind_speed_mnt_avg = calculate_monthly_averages(wind_speed, nr_years)
        wind_direction_mnt_avg = calculate_monthly_averages(
            wind_direction, nr_years)

        # Transform aggregated nc file to geojson
        latitude = nc_file.variables["latitude"][:]
        longitude = nc_file.variables["longitude"][:]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        # Write aggregated wind values to geojson
        wind_speed_features = create_geojson_features(
            latitude, longitude, wind_speed_mnt_avg, months, "speed")
        wind_direction_features = create_geojson_features(
            latitude, longitude, wind_direction_mnt_avg, months, "direction")

        # Write the geojson to files
        with open(path_to_wind_speed, "w") as f:
            dump(wind_speed_features, f)
        with open(path_to_wind_direction, "w") as f:
            dump(wind_direction_features, f)
    finally:
        nc_file.close()  # Close the netCDF file when done


if __name__ == "__main__":

    path_to_input = "../../data/download.nc"
    path_to_wind_speed = "../../data/wind_speed.geojson"
    path_to_wind_direction = "../../data/wind_direction.geojson"
    transform_wind_nc_to_geojson(
        path_to_input, path_to_wind_speed, path_to_wind_direction)
