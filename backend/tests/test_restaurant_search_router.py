"""Tests for restaurants search router"""

from fastapi.testclient import TestClient
from backend.main import app
from backend.app.repositories.restaurant_repo import reset_restaurants

client = TestClient(app)

def setup_function():
    """Reset DB before each test"""
    reset_restaurants()

def test_search_restaurants_endpoint():
    """API should return restaurants matching query"""
    response = client.get("/restaurants/search?q=keg")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "The Keg Steakhouse"

def test_search_menu_items_endpoint():
    """API should return menu items matching query"""
    response = client.get("/restaurants/menu/search?q=roll")

    assert response.status_code == 200
    data = response.json()

    names = [item["name"] for item in data]

    assert "California Roll" in names
