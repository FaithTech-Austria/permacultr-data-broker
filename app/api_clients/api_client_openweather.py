import requests
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_BASE_URL = "https://api.openweathermap.org"
API_KEY_OPENWEATHER = os.getenv("API_KEY_OPENWEATHER")


def get_open_weather_current(lat: float, lon: float):

    url = f"{OPENWEATHER_API_BASE_URL}/data/2.5/forecast?lat={lat}&lon={
        lon}&appid={API_KEY_OPENWEATHER}"

    response = requests.get(url)

    print(response)

    if response.status_code == 200:
        return response.json()
    else:
        return None


if __name__ == "__main__":

    # Define the start and end times
    start_time = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    end_time = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # Calculate the Unix timestamps
    start_unix_timestamp = int(start_time.timestamp())
    end_unix_timestamp = int(end_time.timestamp())

    # define location
    lat = 48.3061
    lon = 14.2867

    weather_data = get_open_weather_current(lat, lon)
    print(weather_data)
