import requests


def get_buildings_from_osmnx(bb) -> dict:
    """access internal osm api to retrieve osm buildings from bounding box"""

    url = "http://osmnx-api:80/buildings/"

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    bb_dict = bb.model_dump()
    response = requests.post(url, headers=headers, json=bb_dict)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Building retrieval from API failed with status code {
                        response.status_code}")
