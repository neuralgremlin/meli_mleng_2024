import pytest
import requests

BASE_URL = "http://localhost:8002"


@pytest.fixture
def get_base_url():
    return BASE_URL


def test_root_endpoint(get_base_url):
    url = f"{get_base_url}/"
    response = requests.get(url)
    assert response.status_code == 404
    assert "detail" in response.json()


def test_anomaly_endpoint(get_base_url):
    url = f"{get_base_url}/anomaly"
    payload = {"PRICE": 21.0, "ITEM_ID": "TEST1"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    assert "ANOMALY" in response.json()
    assert response.json()["ANOMALY"] in [0, 1]
