import numpy as np
from shapely.geometry import Point
import pyproj
import matplotlib.pyplot as plt
import geojson
import requests
from shapely.ops import transform


import numpy as np
import pyproj
from shapely.geometry import Point
from shapely.ops import transform


def reproject_point(point, source_crs, target_crs):
    project = pyproj.Transformer.from_crs(
        source_crs, target_crs, always_xy=True).transform
    reprojected_point = transform(project, point)
    return reprojected_point


def create_regular_grid(bounding_box, point_spacing_metres):
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
        query_url = f"{lat}, {lon}"
        query_urls.append(query_url)

    # create string
    query_string = "|".join(query_urls)
    final_url = base_url + query_string

    # Send a GET request to the API
    response = requests.get(final_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        print(data)
        # Process the API response data as needed
        elev_grid = np.array([result["elevation"]
                             for result in data["results"]])
        return elev_grid
    else:
        return None


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
    bb_list = [47.855281, 14.365568, 47.880206, 14.404243]
    distance_between_points_meter = 500

    # create regular grid
    lat_grid_wgs84, lon_grid_wgs84 = create_regular_grid(
        bb_list, distance_between_points_meter)

    # create coordinate tuples
    grid_points = [(lat, lon) for lat, lon in zip(
        lat_grid_wgs84.flatten(), lon_grid_wgs84.flatten())]

    # get elevation data
    elevation_data = get_elevation_data(grid_points)

    if elevation_data is not None:
        elevation_grid = elevation_data.reshape(lat_grid_wgs84.shape)

        # extract contour lines
        contour_lines = extract_contour_lines(
            lat_grid_wgs84, lon_grid_wgs84, elevation_grid, levels=100)

        # save as geojson
        with open("contour_lines.geojson", "w") as f:
            geojson.dump(contour_lines, f)
