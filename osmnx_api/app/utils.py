import geojson


def graph_to_geojson(graph):
    features = []

    for u, v, data in graph.edges(data=True):
        geometry = data.get('geometry', None)
        if geometry:
            feature = geojson.Feature(
                geometry=geometry,
                properties={'edge_id': f"{u}_{v}"}
            )
            features.append(feature)

    feature_collection = geojson.FeatureCollection(features)
    return feature_collection


def remove_none_values(response: dict) -> dict:
    """removes all the key:pair values where the value is none"""

    if isinstance(response, dict):
        return {key: remove_none_values(value) for key, value in response.items() if value is not None}
    else:
        return response
