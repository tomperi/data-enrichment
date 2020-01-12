import pytest
from ..main import app


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

def test_ping(client):
    ping = client.get("/ping")
    assert ping.data == b"Pong"

def test_invalid_input(client):
    body = {
        "data": [
            {
                "Latitude": "Explorium",
                "Longitude": 144.9051
            }
        ]
    }
    
    response = client.post("api/enrich", json=body)

    assert "Illegal coordinates" in response.json["Errors"][0].get("error")

def test_osm_error(client, requests_mock):
    requests_mock.get("http://www.overpass-api.de/api/xapi", status_code=400)

    body = {
        "data": [
            {
                "Latitude": 32,
                "Longitude": 34,
            }
        ]
    }
    
    response = client.post("api/enrich", json=body)

    assert "Error handling coordinates" in response.json["Errors"][0].get("error")

def test_3_schools(client, requests_mock):
    with open("tests/xml/2_schools.xml", "r") as xml_file:
        xml = "".join([line.strip() for line in xml_file.readlines()])

    requests_mock.get("http://www.overpass-api.de/api/xapi", text=xml)

    body = {
        "data": [
            {
                "Latitude": -37.797,
                "Longitude": 144.9051,
            }
        ]
    }

    response = client.post("api/enrich", json=body)

    assert response.json["data"][0]["Schools"] == 3

def test_2_schools_duplicate(client, requests_mock):
    with open("tests/xml/overlap_way_node.xml", "r") as xml_file:
        xml = "".join([line.strip() for line in xml_file.readlines()])

    requests_mock.get("http://www.overpass-api.de/api/xapi", text=xml)

    body = {
        "data": [
            {
                "Latitude": -37.797,
                "Longitude": 144.9051,
            }
        ]
    }

    response = client.post("api/enrich", json=body)

    assert response.json["data"][0]["Schools"] == 1
