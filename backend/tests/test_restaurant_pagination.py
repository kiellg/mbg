"""Tests for restaurant pagination"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_restaurants_pagination_limit():
    """Restaurants endpoint applies the limit parameter"""
    response = client.get("/restaurants/paginated?page=1&limit=1")

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 1
    assert len(data["items"]) <= 1

def test_restaurants_pagination_second_page():
    """Second page of restaurants should return different results if available"""
    response_page1 = client.get("/restaurants/paginated?page=1&limit=1")
    response_page2 = client.get("/restaurants/paginated?page=2&limit=1")

    assert response_page1.status_code == 200
    assert response_page2.status_code == 200

    data1 = response_page1.json()
    data2 = response_page2.json()

    if data1["items"] and data2["items"]:
        assert data1["items"][0]["id"] != data2["items"][0]["id"]

def test_restaurants_default_pagination():
    """Restaurants endpoint works with default pagination values"""
    response = client.get("/restaurants/paginated")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "page" in data
    assert "limit" in data
    assert "total" in data

def test_menu_pagination_limit():
    """Menu endpoint applies pagination limit"""
    response = client.get("/restaurants/1/menu/paginated?page=1&limit=1")

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 1
    assert len(data["items"]) <= 1

def test_menu_pagination_second_page():
    """Second page of menu items returns different results if available"""
    response_page1 = client.get("/restaurants/1/menu/paginated?page=1&limit=1")
    response_page2 = client.get("/restaurants/1/menu/paginated?page=2&limit=1")

    assert response_page1.status_code == 200
    assert response_page2.status_code == 200

    data1 = response_page1.json()
    data2 = response_page2.json()

    if data1["items"] and data2["items"]:
        assert data1["items"][0]["id"] != data2["items"][0]["id"]

def test_menu_pagination_restaurant_not_found():
    """Menu pagination should return 404 for non existent restaurant"""
    response = client.get("/restaurants/99999/menu/paginated?page=1&limit=5")

    assert response.status_code == 404
