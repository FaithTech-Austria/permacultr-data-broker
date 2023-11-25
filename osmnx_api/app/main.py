from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import osmnx as ox
import json

from app.models import BoundingBox, NetworkTypeValue
from app.utils import graph_to_geojson, remove_none_values

app = FastAPI()


def get_buildings_geojson_from_overpass(bb: dict) -> dict:
    """get buildings from overpass api which are inside bounding box"""

    tags = {'building': True}
    buildings = ox.features_from_bbox(
        bb.max_lat, bb.min_lat, bb.max_lon, bb.min_lon, tags)

    buildings_json = buildings.to_json()
    buildings_geojson = json.loads(buildings_json)
    return buildings_geojson


def get_streets_geojson_from_overpass(bb: dict, network_type: str) -> dict:
    """get streets of certain network type from overpass api which are inside bounding box"""

    streets_graph = ox.graph_from_bbox(bb.max_lat, bb.min_lat,
                                       bb.max_lon, bb.min_lon, network_type=network_type)
    streets_geojson = graph_to_geojson(streets_graph)
    return streets_geojson


def get_waterways_geojson_from_overpass(bb: dict) -> dict:
    """get waterways from overpass api which are inside bb"""

    waterways_graph = ox.graph_from_bbox(bb.max_lat, bb.min_lat,
                                         bb.max_lon, bb.min_lon, retain_all=True, truncate_by_edge=True,
                                         custom_filter='["waterway"~"river"]')
    waterways_geojson = graph_to_geojson(waterways_graph)
    return waterways_geojson


@app.post("/buildings/")
def get_buildings(bb: BoundingBox):
    buildings_geojson = get_buildings_geojson_from_overpass(bb)
    buildings_geojson = remove_none_values(buildings_geojson)
    return buildings_geojson


@app.post("/streets/")
def get_streets(bb: BoundingBox, network_type: NetworkTypeValue):
    streets_geojson = get_streets_geojson_from_overpass(bb, network_type)
    return streets_geojson


@app.post("/waterways/")
def get_waterways(bb: BoundingBox):
    waterways_geojson = get_waterways_geojson_from_overpass(bb)
    return waterways_geojson
