import cdsapi
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

CDS_API_URL = os.getenv("CDS_API_URL")
CDS_API_KEY = os.getenv("CDS_API_KEY")

c = cdsapi.Client(url=CDS_API_URL, key=CDS_API_KEY)


def get_historical_wind_data(path_to_output: str, bounding_box: list, years: list):
    """get monthly averaged wind data of past 5 years 
    File is saved as netcdf in specified directory"""

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
            'area': bounding_box,
            'format': 'netcdf',
        },
        path_to_output)


if __name__ == "__main__":

    # specify input parameters
    today = datetime.date.today()
    years = [str(today.year - i) for i in range(1, 6)]
    bb = []
    path_to_wind_data = "../../data/wind.nc"

    # retrieve wind data from cds
    get_historical_wind_data(path_to_wind_data, bb, years)
