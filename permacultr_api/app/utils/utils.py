from fastapi import HTTPException
from shapely.geometry import Point
from shapely.ops import transform
import pyproj
from app.models import BoundingBox


def wgs84_to_meter_crs(min_lon, min_lat, max_lon, max_lat) -> tuple[float, float, float, float]:

    wgs84_pt_min = Point(min_lon, min_lat)
    wgs84_pt_max = Point(max_lon, max_lat)

    wgs84 = pyproj.CRS('EPSG:4326')
    crs_meters = pyproj.CRS('EPSG:3857')

    project = pyproj.Transformer.from_crs(
        wgs84, crs_meters, always_xy=True).transform

    point_min_meters = transform(project, wgs84_pt_min)
    point_max_meters = transform(project, wgs84_pt_max)

    min_x, min_y = point_min_meters.x, point_min_meters.y
    max_x, max_y = point_max_meters.x, point_max_meters.y

    return min_x, min_y, max_x, max_y


def validate_bounding_box_size(bbox: BoundingBox, max_size_bb_ha: int) -> None:
    """
    Validates the size of a bounding box.

    Args:
        bbox (BoundingBox): The bounding box to validate.
        max_size_bb_ha (int): The maximum allowed size of the bounding box in hectares.

    Raises:
        HTTPException: If the area of the bounding box exceeds the maximum allowed size.

    Returns:
        None
    """
    min_x, min_y, max_x, max_y = wgs84_to_meter_crs(
        bbox.min_lon, bbox.min_lat, bbox.max_lon, bbox.max_lat
    )

    area_meters = (max_x - min_x) * (max_y - min_y)
    area_ha = area_meters / 100000

    if area_ha > max_size_bb_ha:
        raise HTTPException(
            status_code=400, detail=f"Bounding box size exceeds the maximum allowed size of {max_size_bb_ha} hacters"
        )
