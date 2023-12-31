import numpy as np
import subprocess
from osgeo import gdal, osr
import pyproj
import geojson
from shapely.geometry import Point
from shapely.ops import transform


def reproject_point(point: Point, source_crs: pyproj.CRS, target_crs: pyproj.CRS) -> Point:
    project = pyproj.Transformer.from_crs(
        source_crs, target_crs, always_xy=True).transform
    reprojected_point = transform(project, point)
    return reprojected_point


def create_regular_grid(bounding_box: dict, point_spacing_metres: int) -> tuple:

    wgs84 = pyproj.CRS("EPSG:4326")
    web_mercator = pyproj.CRS("EPSG:3857")

    point_lat_lon_min_4326 = Point(bounding_box.min_lat, bounding_box.min_lon)
    point_lat_lon_max_4326 = Point(bounding_box.max_lat, bounding_box.max_lon)

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

    # for latitude lowest values in first row, for longitude lowest values in first column
    lon_grid_wgs84 = np.rot90(lon_grid_wgs84)
    lat_grid_wgs84 = np.flip(np.rot90(lat_grid_wgs84), axis=0)

    return (lat_grid_wgs84, lon_grid_wgs84)


def extract_elevation_data(json_data) -> dict:
    # Extract latitude, longitude, and elevation values from the JSON data

    latitudes = [entry['location']['lat'] for entry in json_data['results']]
    longitudes = [entry['location']['lng'] for entry in json_data['results']]
    elevations = [entry['elevation'] for entry in json_data['results']]

    data = {}
    for lon, lat, elev in zip(longitudes, latitudes, elevations):
        data[(lon, lat)] = elev

    return data


def create_elevation_points_geojson(elevation_data: dict[(float, float), float], path_to_output: str) -> None:

    # Create a list of GeoJSON features
    features = []
    for (lon, lat), elevation in elevation_data.items():
        point = geojson.Point((lon, lat))
        properties = {'elevation': elevation}
        feature = geojson.Feature(geometry=point, properties=properties)
        features.append(feature)

    # Create a GeoJSON feature collection
    feature_collection = geojson.FeatureCollection(features)

    # Save the feature collection as a GeoJSON file
    with open(path_to_output, 'w') as geojson_file:
        geojson.dump(feature_collection, geojson_file,
                     sort_keys=True, ensure_ascii=False)


def create_elevation_raster(lon_arr: np.array, lat_arr: np.array, elevation_data: dict, path_to_output: str) -> None:
    """create a elevation raster and save as geotiff based on a regular grid with corresponding elevation data"""

    def custom_get(x, y):
        return elevation_data[(x, y)]

    # Use np.vectorize with the custom_get function
    vfunc = np.vectorize(custom_get)
    elevation_arr = vfunc(lon_arr, lat_arr)
    elevation_arr = np.flip(elevation_arr, axis=0)

    # Calculate pixel width and pixel height based on your arrays
    pixel_width = (lon_arr[0, 1] - lon_arr[0, 0])
    pixel_height = (lat_arr[1, 0] - lat_arr[0, 0])
    image_width = lon_arr.shape[1]
    image_height = lat_arr.shape[0]

    # Create a new GeoTIFF dataset
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(path_to_output, image_width,
                            image_height, 1, gdal.GDT_Float32)
    srs = osr.SpatialReference()

    # Replace with the appropriate EPSG code for your data
    srs.ImportFromEPSG(4326)
    dataset.SetProjection(srs.ExportToWkt())

    # specify offset
    offset_lon = pixel_width / 2
    offset_lat = pixel_height / 2

    geotransform = (lon_arr[0, 0] - offset_lon, pixel_width, 0,
                    lat_arr[-1, 0] + offset_lat, 0, -pixel_height)
    dataset.SetGeoTransform(geotransform)

    # Write the values to the GeoTIFF
    band = dataset.GetRasterBand(1)
    band.WriteArray(elevation_arr)

    # Close the dataset to save the GeoTIFF
    dataset = None

    # Use subprocess to compress the GeoTIFF using GDAL utilities (optional)
    path_to_output_comp = path_to_output.replace(".tif", "_comp.tif")
    subprocess.call(['gdal_translate', '-of', 'GTiff', '-co',
                    'COMPRESS=LZW', path_to_output, path_to_output_comp])


def create_contour_lines_geojson(path_to_elevation_grid: str, path_to_output: str, contour_interval: int) -> None:
    """create contour line vector data based on elevation raster"""

    gdal_contour_command = [
        "gdal_contour",
        "-a", "elevation",
        "-i", str(contour_interval),
        "-snodata", "0",
        path_to_elevation_grid,
        path_to_output
    ]

    subprocess.run(gdal_contour_command, check=True)


if __name__ == "__main__":

    # bb_list = [47.060994, 15.414642, 47.085363, 15.455275]
    # distance_between_points_meter = 400
    # contour_interval = 10

    pass
