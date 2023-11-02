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
        # Process the API response data as needed
        elev_grid = np.array([result["elevation"]
                             for result in data["results"]])
        return elev_grid
    else:
        return None


def vertex_on_boundary(vertex: list, bounds: list) -> bool:
    """check if point is on boundary"""
    lat_max, lat_min, lon_max, lon_min = bounds
    return (vertex[0] == lat_max) | (vertex[0] == lat_min) | (vertex[1] == lon_max) | (vertex[1] == lon_min)


def crosses_existing_lines(line: LineString, existing_lines: list[LineString]) -> bool:
    """check if line crosses with any other lines in the lists"""
    return any(line.crosses(other_line) for other_line in existing_lines)


def extract_contour_lines(lat_grid: np.array, lon_grid: np.array, elev_grid: np.array, levels: int | list) -> dict:
    """get contour lines from regular point grid and convert to geojson format"""

    lat_max, lat_min, lon_max, lon_min = np.amax(lat_grid), np.amin(
        lat_grid), np.amax(lon_grid), np.amin(lon_grid)
    bounds = [lat_max, lat_min, lon_max, lon_min]

    cs = plt.contour(lat_grid, lon_grid, elev_grid, levels=levels)

    contour_lines = []
    all_lines = []
    vertices_first_list, vertices_second_list = [], []

    for i, collection in enumerate(cs.collections):
        elevation = cs.levels[i]
        for path in collection.get_paths():
            vertices = [vertex.tolist() for vertex in path.vertices]
            for i, j in zip(range(0, len(vertices)), range(1, len(vertices))):

                vertices_first_list.append(vertices[i])
                vertices_second_list.append(vertices[j])
                line = LineString([vertices[i], vertices[j]])
                all_lines.append(line)
                contour_lines.append(geojson.Feature(
                    geometry=geojson.LineString(
                        [vertices[i], vertices[j]]),
                    properties={"elevation": elevation}
                ))

    remove_idx = []
    for i in range(len(all_lines)):
        vertex_first = vertices_first_list[i]
        vertex_second = vertices_second_list[i]
        line = all_lines[i]

        if crosses_existing_lines(line, all_lines) & (vertex_on_boundary(vertex_first, bounds)) & (vertex_on_boundary(vertex_second, bounds)):
            remove_idx.append(i)

    lines_reduced = list(np.delete(np.array(all_lines), remove_idx))

    for i in range(len(all_lines)):
        vertex_first = vertices_first_list[i]
        vertex_second = vertices_second_list[i]
        line = all_lines[i]

        if crosses_existing_lines(line, lines_reduced) & ((vertex_on_boundary(vertices_first_list[i], bounds)) | (vertex_on_boundary(vertex_second, bounds))):
            remove_idx.append(i)

    contour_lines = list(np.delete(np.array(contour_lines), remove_idx))
    feature_collection = geojson.FeatureCollection(contour_lines)
    return feature_collection


if __name__ == "__main__":

    # specify bounding box and spacing between points in regular grid
    bb_list = [48.289416, 14.263430, 48.315876, 14.314499]
    bb_list = [47.855281, 14.365568, 47.880206, 14.404243]
    bb_list = [47.060994, 15.414642, 47.085363, 15.455275]

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
            lat_grid_wgs84, lon_grid_wgs84, elevation_grid, levels=20)

        # save as geojson
        with open("contour_lines.geojson", "w") as f:
            geojson.dump(contour_lines, f)
