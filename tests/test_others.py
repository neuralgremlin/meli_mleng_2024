import pytest
import requests

BASE_URL = "http://localhost:"

@pytest.fixture
def get_base_url():
    return BASE_URL


def test_mongo_up(get_base_url):
    url = f"{get_base_url}27017/"
    response = requests.get(url)
    assert response.status_code == 200

def test_grafana_up(get_base_url):
    url = f"{get_base_url}3000/"
    response = requests.get(url)
    assert response.status_code == 200

def test_prometheus(get_base_url):
    url = f"{get_base_url}9090/"
    response = requests.get(url)
    assert response.status_code == 200