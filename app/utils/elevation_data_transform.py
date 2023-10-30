import json
import numpy as np
from scipy.interpolate import griddata
from geojson import Feature, FeatureCollection, LineString


def access_elevation_data(bounding_box: list):
    pass


def extract_coordinates(elevation_data):
    return zip(*((point['x'], point['y'], point['z']) for point in elevation_data))


def create_regular_grid(x_coords, y_coords):
    x_min, x_max, y_min, y_max = min(x_coords), max(
        x_coords), min(y_coords), max(y_coords)
    return np.mgrid[x_min:x_max:100j, y_min:y_max:100j]


def interpolate_elevation(x_coords, y_coords, z_coords, grid_x, grid_y):
    return griddata((x_coords, y_coords), z_coords, (grid_x, grid_y), method='cubic')


def generate_contour_lines(grid_z, contour_levels, grid_x, grid_y):
    contour_features = []
    for contour_level in contour_levels:
        contour = grid_z > contour_level
        contour_edges = np.where(np.diff(contour), 1, 0)
        contour_rows, contour_cols = contour_edges.nonzero()

        contour_lines = [LineString([(grid_x[row, col], grid_y[row, col]),
                                    (grid_x[row, col + 1], grid_y[row, col + 1])])
                         for row, col in zip(contour_rows, contour_cols)]

        contour_feature = Feature(geometry=contour_lines, properties={
                                  "elevation": contour_level})
        contour_features.append(contour_feature)

    contour_collection = FeatureCollection(contour_features)

    return contour_collection


if __name__ == "__main__":
    bounding_box = []
    elevation_data = access_elevation_data(bounding_box)
    x_coords, y_coords, z_coords = extract_coordinates(elevation_data)
    grid_x, grid_y = create_regular_grid(x_coords, y_coords)
    grid_z = interpolate_elevation(
        x_coords, y_coords, z_coords, grid_x, grid_y)
    contour_levels = [10, 20, 30, 40]
    contour_features = generate_contour_lines(
        grid_z, contour_levels, grid_x, grid_y)
