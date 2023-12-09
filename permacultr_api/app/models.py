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


class AgroclimaticIndicator(str, Enum):
    """Selection fo agroclimatic indicators to choose from"""
    biologically_effective_degree_days = "biologically_effective_degree_days"
    frost_days = "frost_days"
    heavy_precipitation_days = "heavy_precipitation_days"
    ice_days = "ice_days"
    maximum_of_daily_maximum_temperature = "maximum_of_daily_maximum_temperature"
    maximum_of_daily_minimum_temperature = "maximum_of_daily_minimum_temperature"
    mean_of_daily_maximum_temperature = "mean_of_daily_maximum_temperature"
    mean_of_daily_mean_temperature = "mean_of_daily_mean_temperature"
    mean_of_daily_minimum_temperature = "mean_of_daily_minimum_temperature"
    mean_of_diurnal_temperature_range = "mean_of_diurnal_temperature_range"
    minimum_of_daily_maximum_temperature = "minimum_of_daily_maximum_temperature"
    minimum_of_daily_minimum_temperature = "minimum_of_daily_minimum_temperature"
    precipitation_sum = "precipitation_sum"
    simple_daily_intensity_index = "simple_daily_intensity_index"
    summer_days = "summer_days"
    tropical_nights = "tropical_nights"
    very_heavy_precipitation_days = "very_heavy_precipitation_days"
    wet_days = "wet_days"
