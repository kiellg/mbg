"""Tests for restaurant filter router endpoint"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_filter_restaurants_router_returns_list():
    """GET /restaurants/filter should return a list"""
    response = client.get("/restaurants/filter?cuisine_types=italian")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for restaurant in data:
        assert restaurant["cuisine_type"] == "italian"

def test_filter_restaurants_router_multiple_cuisines():
    """Router should accept multiple cuisine filters"""
    response = client.get(
        "/restaurants/filter?cuisine_types=italian&cuisine_types=japanese"
    )

    assert response.status_code == 200

def test_filter_restaurants_router_no_filter():
    """GET /restaurants/filter without params should still work"""
    response = client.get("/restaurants/filter")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
