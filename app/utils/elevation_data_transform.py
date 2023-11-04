import numpy as np
from shapely.geometry import Point, LineString
import pyproj
import matplotlib.pyplot as plt
import geojson
import requests
from shapely.ops import transform
import numpy as np
import pyproj
from shapely.geometry import Point
from shapely.ops import transform

import subprocess
from osgeo import gdal, osr


def reproject_point(point: Point, source_crs: pyproj.CRS, target_crs: pyproj.CRS) -> Point:
    project = pyproj.Transformer.from_crs(
        source_crs, target_crs, always_xy=True).transform
    reprojected_point = transform(project, point)
    return reprojected_point


def create_regular_grid(bounding_box: list, point_spacing_metres: int) -> tuple:
    wgs84 = pyproj.CRS("EPSG:4326")
    web_mercator = pyproj.CRS("EPSG:3857")

    point_lat_lon_min_4326 = Point(bounding_box[0], bounding_box[1])
    point_lat_lon_max_4326 = Point(bounding_box[2], bounding_box[3])

    point_lat_lon_min_3857 = reproject_point(
        point_lat_lon_min_4326, wgs84, web_mercator)
    point_lat_lon_max_3857 = reproject_point(
        point_lat_lon_max_4326, wgs84, web_mercator)

    lat_min, lon_min = point_lat_lon_min_3857.xy[1][0], point_lat_lon_min_3857.xy[0][0]
    lat_max, lon_max = point_lat_lon_max_3857.xy[1][0], point_lat_lon_max_3857.xy[0][0]

    lat_points = np.arange(lat_min, lat_max, point_spacing_metres)
    lon_points = np.arange(lon_min, lon_max, point_spacing_metres)
    lon_grid_3857, lat_grid_3857 = np.meshgrid(lon_points, lat_points)

    transformer = pyproj.Transformer.from_crs(
        web_mercator, wgs84, always_xy=True)
    lon_grid_wgs84, lat_grid_wgs84 = transformer.transform(
        lon_grid_3857, lat_grid_3857)

    return (lat_grid_wgs84, lon_grid_wgs84)


def get_elevation_data(locations: list) -> np.array:
    """get elevation data for a lit of coordinate tuples"""

    base_url = "https://api.opentopodata.org/v1/srtm90m?locations="

    # Generate query URLs for each location
    query_urls = []
    for lon, lat in locations:
        query_url = f"{lon}, {lat}"
        query_urls.append(query_url)

    # create string
    query_string = "|".join(query_urls)
    final_url = base_url + query_string

    # Send a GET request to the API
    response = requests.get(final_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Elevation retrieval from API did not work")
        return None


def create_arrays_from_json(json_data):
    # Extract latitude, longitude, and elevation values from the JSON data

    latitudes = [entry['location']['lat'] for entry in json_data['results']]
    longitudes = [entry['location']['lng'] for entry in json_data['results']]
    elevations = [entry['elevation'] for entry in json_data['results']]

    data = {}
    for lon, lat, elev in zip(longitudes, latitudes, elevations):
        data[(lon, lat)] = elev

    return data


if __name__ == "__main__":

    # specify bounding box and spacing between points in regular grid
    bb_list = [48.289416, 14.263430, 48.315876, 14.314499]
    bb_list = [47.855281, 14.365568, 47.880206, 14.404243]
    # bb_list = [47.060994, 15.414642, 47.085363, 15.455275]
    bb_list = [-13.526504, -72.013784, -13.491379, -71.965204]

    distance_between_points_meter = 1000

    # create regular grid
    lon_grid_wgs84, lat_grid_wgs84 = create_regular_grid(
        bb_list, distance_between_points_meter)

    lon_grid_wgs84 = np.rot90(lon_grid_wgs84)
    lat_grid_wgs84 = np.flip(np.rot90(lat_grid_wgs84), axis=0)

    # create coordinate tuples
    grid_points = [(lat, lon) for lat, lon in zip(
        lat_grid_wgs84.flatten(), lon_grid_wgs84.flatten())]

    # get elevation data
    elevation_data = get_elevation_data(grid_points)
    elevation_data_orderered = create_arrays_from_json(elevation_data)

    # Create a list of GeoJSON features
    features = []
    for (lon, lat), elevation in elevation_data_orderered.items():
        point = geojson.Point((lon, lat))
        properties = {'elevation': elevation}
        feature = geojson.Feature(geometry=point, properties=properties)
        features.append(feature)

    # Create a GeoJSON feature collection
    feature_collection = geojson.FeatureCollection(features)

    # Save the GeoJSON feature collection to a file
    with open('elevation_data.geojson', 'w') as file:
        geojson.dump(feature_collection, file,
                     sort_keys=True, ensure_ascii=False)

    def custom_get(x, y):
        return elevation_data_orderered[(x, y)]

    # Use np.vectorize with the custom_get function
    vfunc = np.vectorize(custom_get)
    elevation_grid = vfunc(lon_grid_wgs84, lat_grid_wgs84)

    # Define the output GeoTIFF file path
    output_tiff_path = "output.tif"

    longitude = lon_grid_wgs84
    latitude = lat_grid_wgs84
    values = np.flip(elevation_grid, axis=0)

    # Calculate pixel width and pixel height based on your arrays
    pixel_width = (longitude[0, 1] - longitude[0, 0])
    pixel_height = (latitude[1, 0] - latitude[0, 0])
    image_width = longitude.shape[1]
    image_height = latitude.shape[0]

    # Create a new GeoTIFF dataset
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(output_tiff_path, image_width,
                            image_height, 1, gdal.GDT_Float32)
    srs = osr.SpatialReference()
    # Replace with the appropriate EPSG code for your data
    srs.ImportFromEPSG(4326)
    dataset.SetProjection(srs.ExportToWkt())

    offset_lon = pixel_width / 2
    offset_lat = pixel_height / 2

    geotransform = (longitude[0, 0] - offset_lon, pixel_width, 0,
                    latitude[-1, 0] + offset_lat, 0, -pixel_height)
    dataset.SetGeoTransform(geotransform)

    # Write the values to the GeoTIFF
    band = dataset.GetRasterBand(1)
    band.WriteArray(values)

    # Close the dataset to save the GeoTIFF
    dataset = None

    # Use subprocess to compress the GeoTIFF using GDAL utilities (optional)
    subprocess.call(['gdal_translate', '-of', 'GTiff', '-co',
                    'COMPRESS=LZW', output_tiff_path, 'compressed_output.tif'])

    # Replace with the desired output file name and format
    output_contour_geojson = "contour_lines.geojson"

    # Define the contour interval (e.g., 10) and other options as needed
    contour_interval = 10

    # Build the gdal_contour command
    gdal_contour_command = [
        "gdal_contour",
        "-a", "elevation",  # Attribute field name
        "-i", str(contour_interval),  # Contour interval
        "-snodata", "0",  # NoData value
        output_tiff_path,  # Input GeoTIFF file
        output_contour_geojson,  # Output contour Shapefile
    ]

    # Execute the gdal_contour command
    try:
        subprocess.run(gdal_contour_command, check=True)
        print("Contour lines generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate contour lines. Error: {e}")
