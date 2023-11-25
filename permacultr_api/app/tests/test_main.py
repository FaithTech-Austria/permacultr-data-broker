from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_bounding_box_size_checking_for_buildings():
    response = client.post(
        "/api/osm/buildings/",
        json={
            "bb": {
                "min_longitude": 10.0,
                "min_latitude": 45.0,
                "max_longitude": 11.0,
                "max_latitude": 46.0
            }
        }
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Bounding box size exceeds the maximum allowed size of 1 hacters"
    }
