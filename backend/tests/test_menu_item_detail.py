"""Tests for menu item detail endpoint"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_menu_item_detail_success():
    """Should return full menu item detail with formatted price"""
    response = client.get("/restaurants/1/menu/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Ribeye Steak"
    assert data["restaurant_id"] == 1

    assert data["description"] != ""
    assert data["display_price"] is not None
    assert data["price_status"] == "ok"

    assert data["is_available"] is True

def test_get_menu_item_detail_missing_price():
    """Should handle missing price correctly"""
    response = client.get("/restaurants/1/menu/4")

    assert response.status_code == 200

    data = response.json()

    assert data["price_status"] == "missing"
    assert data["display_price"] is None

def test_get_menu_item_detail_invalid_price():
    """Should handle invalid price"""
    response = client.get("/restaurants/1/menu/3")

    assert response.status_code == 200

    data = response.json()

    assert data["price_status"] == "invalid"
    assert data["display_price"] is None

def test_get_menu_item_detail_not_visible_or_inactive():
    """Should hide price if item is not visible"""
    response = client.get("/restaurants/1/menu/2")

    assert response.status_code == 200

    data = response.json()

    assert data["display_price"] is not None

def test_get_menu_item_detail_category_formatting():
    """Should return formatted category name"""
    response = client.get("/restaurants/1/menu/1")

    assert response.status_code == 200

    data = response.json()

    assert data["category"] is not None
    assert "id" in data["category"]
    assert "name" in data["category"]

def test_get_menu_item_detail_item_not_found():
    """Should return 404 if menu item does not exist"""
    response = client.get("/restaurants/1/menu/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found"

def test_get_menu_item_detail_restaurant_not_found():
    """Should return 404 if restaurant doesn't exist"""
    response = client.get("/restaurants/999/menu/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"
