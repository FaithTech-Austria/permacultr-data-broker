import netCDF4 as nc
import numpy as np
from geojson import Feature, Point, FeatureCollection, dump
import os

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


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


def create_feature_collection(latitude, longitude, data, months=MONTHS):
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


def create_wind_geojson(path_to_wind_nc_file: str, wind_property: str, years: list):

    nc_file = nc.Dataset(path_to_wind_nc_file)

    try:
        u10, v10 = read_nc_variables(nc_file)

        # Calculate wind speed and direction
        wind_speed, wind_direction = calculate_wind_properties(u10, v10)

        # Calculate monthly average of wind speed and direction
        # TODO nr_years not solved very elegantly
        nr_years = int(wind_speed.shape[0] / 12)
        if wind_property == "speed":
            wind_mnt_avg = calculate_monthly_averages(wind_speed, nr_years)
        elif wind_property == "direction":
            wind_mnt_avg = calculate_monthly_averages(wind_direction, nr_years)

        print(f"Hello: {wind_property}")

        # Transform aggregated nc file to geojson
        latitude = nc_file.variables["latitude"][:]
        longitude = nc_file.variables["longitude"][:]

        wind_property_features = create_feature_collection(
            latitude, longitude, wind_mnt_avg)
        wind_property_features["name"] = wind_property
        wind_property_features["description"] = f"Monthly averages over the last {
            len(years)} years"
        return wind_property_features

    finally:
        nc_file.close()
