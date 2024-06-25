import pytest
import requests

BASE_URL = "http://localhost:8001"


@pytest.fixture
def get_base_url():
    return BASE_URL


def test_root_endpoint(get_base_url):
    url = f"{get_base_url}/"
    response = requests.get(url)
    assert response.status_code == 200
    assert response.json()["message"] == "HELLO WORLD FROM DB-CLIENT"


def test_upload_endpoint(get_base_url):
    url = f"{get_base_url}/uploadcsv"
    # Prueba de inserción de CSV
    response = requests.post(url, files={"file": open("./tests/upload_test.csv", "rb")})
    assert response.status_code == 200


def test_get_items_no_exists(get_base_url):
    url = f"{get_base_url}/item_history/TEST0"
    response = requests.get(url)
    assert response.status_code == 200
    assert "documents" in response.json()
    assert len(response.json()["documents"]) == 0


def test_get_items_exists(get_base_url):
    url = f"{get_base_url}/item_history/TEST1"
    response = requests.get(url)
    assert response.status_code == 200
    assert "documents" in response.json()
    assert len(response.json()["documents"]) == 3
