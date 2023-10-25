import cdsapi
from dotenv import load_dotenv
import os

load_dotenv()

CDS_API_URL = os.getenv("CDS_API_URL")
CDS_API_KEY = os.getenv("CDS_API_KEY")

c = cdsapi.Client(url=CDS_API_URL, key=CDS_API_KEY)


c.retrieve(
    'reanalysis-era5-land-monthly-means',
    {
        'product_type': 'monthly_averaged_reanalysis',
        'variable': [
            '10m_u_component_of_wind', '10m_v_component_of_wind',
        ],
        'year': [
            '2019', '2020', '2021',
            '2022',
        ],
        'month': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
        ],
        'time': '00:00',
        'area': [
            65, 40, 60,
            50,
        ],
        'format': 'netcdf',
    },
    '../../data/download.nc')
