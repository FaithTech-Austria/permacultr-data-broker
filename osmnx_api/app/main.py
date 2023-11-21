from fastapi import FastAPI
import osmnx as ox
from app.models import BoundingBox
import json

app = FastAPI()


def get_buildings_geojson_from_overpass(bb: dict) -> dict:
    """get buildings from overpass api which are inside bounding box"""

    tags = {'building': True}
    buildings = ox.features_from_bbox(
        bb.max_lat, bb.min_lat, bb.max_lon, bb.min_lon, tags)

    buildings_json = buildings.to_json()
    buildings_geojson = json.loads(buildings_json)
    return buildings_geojson


def remove_none_values(response: dict) -> dict:
    """removes all the key:pair values where the value is none"""

    if isinstance(response, dict):
        return {key: remove_none_values(value) for key, value in response.items() if value is not None}
    else:
        return response


@app.post("/buildings/")
def get_buildings(bb: BoundingBox):
    buildings_geojson = get_buildings_geojson_from_overpass(bb)
    buildings_geojson = remove_none_values(buildings_geojson)
    return buildings_geojson
