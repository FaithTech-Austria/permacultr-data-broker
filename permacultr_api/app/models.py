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


class WindParameterValue(str, Enum):
    speed = "speed"
    direction = "direction"


class ContourInterval(BaseModel):
    value: int


class Resolution(BaseModel):
    value: int
