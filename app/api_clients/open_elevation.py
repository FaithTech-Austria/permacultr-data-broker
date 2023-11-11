import requests
import numpy as np


def get_elevation_data(locations: list[(float, float)]) -> np.array:
    """get elevation data for a lit of coordinate tuples"""

    base_url = "http://open-elevation:8080/api/v1/lookup?locations="

    # Generate query URLs for each location
    query_urls = []
    for lon, lat in locations:
        query_url = f"{lon},{lat}"
        query_urls.append(query_url)

    # create string
    query_string = "|".join(query_urls)
    final_url = base_url + query_string

    # Send a GET request to the API
    response = requests.get(final_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # restructuring of elevation data
        for elev_point in data["results"]:
            elev_point["location"] = {}
            elev_point["location"]["lat"] = elev_point["latitude"]
            elev_point["location"]["lng"] = elev_point["longitude"]
            del elev_point["latitude"]
            del elev_point["longitude"]

        return data
    else:
        raise Exception(f"Elevation retrieval from API failed with status code {
                        response.status_code}")


if __name__ == "__main__":

    data = get_elevation_data([(-4.8, 30), (-4.8, 30), (-4.8, 30)])
    print(data)
