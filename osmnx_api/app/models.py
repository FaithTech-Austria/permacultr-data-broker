from pydantic import BaseModel
from enum import Enum


class BoundingBox(BaseModel):
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float


class NetworkTypeValue(str, Enum):
    drive = "drive"
    walk = "walk"
