import datetime
from api_clients.cds import get_historical_wind_data
from utils.data_transform import transform_wind_nc_to_geojson


if __name__ == "__main__":

    # specify paths
    path_to_wind_data_nc = "../data/wind_linz.nc"
    path_to_wind_speed_agg = "../data/wind_speed_linz.geojson"
    path_to_wind_direction_agg = "../data/wind_direction_linz.geojson"

    # define parameters
    today = datetime.date.today()
    years = [str(today.year - i) for i in range(1, 6)]
    bb = [48.272926, 14.250641, 48.315057, 14.327202]

    # download data from CDS
    get_historical_wind_data(path_to_wind_data_nc, bb, years)

    # transform wind data to aggregated direction and speed and save as geojson
    transform_wind_nc_to_geojson(
        path_to_wind_data_nc, path_to_wind_speed_agg, path_to_wind_direction_agg)
