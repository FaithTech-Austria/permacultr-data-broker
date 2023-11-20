from fastapi import FastAPI
import osmnx as ox
from app.models import BoundingBox
import json

app = FastAPI()


@app.post("/")
def pong():
    return {"ping": "pong"}


def get_buildings_geojson_from_overpass(bb: dict) -> dict:

    tags = {'building': True}

    buildings = ox.features_from_bbox(
        bb.max_lat, bb.min_lat, bb.max_lon, bb.min_lon, tags)

    buildings_json = buildings.to_json()
    buildings_geojson = json.loads(buildings_json)
    return buildings_geojson


@app.post("/buildings/")
def get_buildings(bb: BoundingBox):

    buildings_geojson = get_buildings_geojson_from_overpass(bb)
    print(type(buildings_geojson))

    return buildings_geojson
