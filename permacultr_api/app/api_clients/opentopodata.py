import requests
import numpy as np


def get_elevation_data(locations: list[(float, float)]) -> np.array:
    """get elevation data for a lit of coordinate tuples"""

    base_url = "https://api.opentopodata.org/v1/srtm90m?locations="

    # Generate query URLs for each location
    query_urls = []
    for lon, lat in locations:
        query_url = f"{lon}, {lat}"
        query_urls.append(query_url)

    # create string
    query_string = "|".join(query_urls)
    final_url = base_url + query_string

    # Send a GET request to the API
    response = requests.get(final_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Elevation retrieval from API failed with status code {
                        response.status_code}")


if __name__ == "__main__":

    expected_output_structure = {
        "results": [
            {
                "dataset": "srtm30m",
                "elevation": 1604.0,
                "location": {
                    "lat": 39.747114,
                    "lng": -104.996334
                }
            }
        ],
        "status": "OK"
    }
