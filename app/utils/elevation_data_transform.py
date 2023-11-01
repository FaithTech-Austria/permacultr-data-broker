import numpy as np
from shapely.geometry import Point
import pyproj
import matplotlib.pyplot as plt
import geojson


def reproject_point(point: Point, source_crs: pyproj.CRS, target_crs: pyproj.CRS) -> Point:
    """transforms a shapely point from source to target projection. Returns shapely Point"""

    transformer = pyproj.Transformer.from_crs(
        source_crs, target_crs, always_xy=True)
    return transformer.transform(point)


def create_regular_grid(bounding_box: list, point_spacing_metres: int) -> tuple:
    """create a regular point grid within a bounding box and spacing defined by point_spacing_metres"""

    # define source and target crs
    wgs84 = pyproj.CRS("EPSG:4326")
    web_mercator = pyproj.CRS("EPSG:3857")

    # extract corner points from bounding box
    point_lat_lon_min_4326 = Point(bounding_box[0], bounding_box[1])
    point_lat_lon_max_4326 = Point(bounding_box[2], bounding_box[3])

    # reproject corner points to web mercator projection
    point_lat_lon_min_3857 = reproject_point(
        point_lat_lon_min_4326, wgs84, web_mercator)
    point_lat_lon_max_3857 = reproject_point(
        point_lat_lon_max_4326, wgs84, web_mercator)

    # create point grid, where distance between points is point_spacing_metres
    lat_min, lon_min = point_lat_lon_min_3857.xy[0][0], point_lat_lon_min_3857.xy[1][0]
    lat_max, lon_max = point_lat_lon_max_3857.xy[0][0], point_lat_lon_max_3857.xy[1][0]
    lat_points = np.arange(lat_min, lat_max, point_spacing_metres)
    lon_points = np.arange(lon_min, lon_max, point_spacing_metres)
    lon_grid_3857, lat_grid_3857 = np.meshgrid(lon_points, lat_points)

    # transform point grid back to wegs84
    transformer = pyproj.Transformer.from_crs(
        web_mercator, wgs84, always_xy=True)
    lon_grid_wgs84, lat_grid_wgs84 = transformer.transform(
        lon_grid_3857, lat_grid_3857)

    return lat_grid_wgs84, lon_grid_wgs84


def get_elevation_data(point: list) -> np.array:
    """get elevation data for a lit of coordinate tuples"""

    elevation = np.zeros(lat_grid_wgs84.shape)
    return elevation


def extract_contour_lines(lat_grid: np.array, lon_grid: np.array, elev_grid: np.array, levels: int | list) -> dict:
    """get contour lines from regular point grid and convert to geojson format"""

    cs = plt.contour(lat_grid, lon_grid, elev_grid, levels=levels)
    contour_lines = []

    # Extract contour data and create LineString geometries
    for i, collection in enumerate(cs.collections):
        elevation = cs.levels[i]
        for path in collection.get_paths():
            coordinates = [vertex.tolist() for vertex in path.vertices]
            if coordinates:
                contour_lines.append(geojson.Feature(
                    geometry=geojson.LineString(coordinates),
                    properties={"elevation": elevation}
                ))

    # Create a GeoJSON feature collection
    feature_collection = geojson.FeatureCollection(contour_lines)
    return feature_collection


if __name__ == "__main__":

    # specify bounding box and spacing between points in regular grid
    bb_list = [48.289416, 14.263430, 48.315876, 14.314499]
    distance_between_points_meter = 30

    # create regular grid
    lat_grid_wgs84, lon_grid_wgs84 = create_regular_grid(
        bb_list, distance_between_points_meter)

    # create coordinate tuples
    grid_points = [(lat, lon) for lat, lon in zip(
        lat_grid_wgs84.flatten(), lon_grid_wgs84.flatten())]

    # get elevation data
    elevation_grid = get_elevation_data(grid_points)

    # extract contour lines
    contour_lines = extract_contour_lines(
        lat_grid_wgs84, lon_grid_wgs84, elevation_grid, levels=10)

    # save as geojson
    with open("contour_lines.geojson", "w") as f:
        geojson.dump(contour_lines, f)
