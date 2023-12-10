from pydantic import BaseModel
from enum import Enum


class BoundingBox(BaseModel):
    """Bounding Box coordinates"""
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float


class NetworkTypeValue(str, Enum):
    """Choosing between drive and walk ways"""
    drive = "drive"
    walk = "walk"


class WindParameterValue(str, Enum):
    """speed wind or direction"""
    speed = "speed"
    direction = "direction"


class ContourInterval(BaseModel):
    """meters between contour lines"""
    value: int


class Resolution(BaseModel):
    """resolution of DEM from which contour lines are derived"""
    value: int


# TODO extent class
class AgroclimaticIndicator(str, Enum):
    """Selection fo agroclimatic indicators to choose from"""
    biologically_effective_degree_days = "biologically_effective_degree_days"
