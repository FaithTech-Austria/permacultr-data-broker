import requests


def get_data_from_osmnx(bb: dict, data: str, network_type: str | None = None) -> requests.Response:

    url = f"http://osmnx-api:80/{data}/"

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    bb_dict = bb.model_dump()

    if network_type:
        url = f"{url}?network_type={network_type}"

    response = requests.post(url, headers=headers, json=bb_dict)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Building retrieval from API failed with status code {
                        response.status_code}")
