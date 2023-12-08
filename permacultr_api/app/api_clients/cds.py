import cdsapi
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

CDS_API_URL = os.getenv("CDS_API_URL")
CDS_API_KEY = os.getenv("CDS_API_KEY")

c = cdsapi.Client(url=CDS_API_URL, key=CDS_API_KEY)


def get_historical_wind_data(path_to_output: str, bounding_box: dict, years: list) -> None:
    """get monthly averaged wind data of past 5 years 
    File is saved as netcdf in specified directory"""

    bb_list = [bounding_box.min_lat, bounding_box.min_lon,
               bounding_box.max_lat, bounding_box.max_lon]

    c.retrieve(
        'reanalysis-era5-land-monthly-means',
        {
            'product_type': 'monthly_averaged_reanalysis',
            'variable': [
                '10m_u_component_of_wind', '10m_v_component_of_wind',
            ],
            'year': years,
            'month': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12'
            ],
            'time': '00:00',
            'area': bb_list,
            'format': 'netcdf',
        },
        path_to_output)


def get_agroclimatic_indicator(path_to_output: str, parameter: str) -> None:
    """
    Downloads 
    Agroclimatic indicators 
    https://cds.climate.copernicus.eu/cdsapp#!/dataset/sis-agroclimatic-indicators?tab=overview
    output must be a zip or tar.gz
    """

    c.retrieve(
        'sis-agroclimatic-indicators',
        {
            'format': 'zip',
            'origin': 'era_interim_reanalysis',
            'variable': parameter,
            'experiment': 'historical',
            'temporal_aggregation': '10_day',
            'period': '198101_201012',
            'version': '1.1',
        },
        path_to_output)
