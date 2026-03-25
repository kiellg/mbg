"""Tests for the restaurant menu endpoint"""

import pytest
from fastapi.testclient import TestClient
from app.repositories import restaurant_repo
from main import app

client = TestClient(app)

def setup_function():
    """Reset all in-memory state before each test"""
    restaurant_repo.reset_restaurants()

def test_restaurant_menu_returns_200():
    """GET /restaurants/{id}/menu should return 200 with menu data"""
    r = client.get("/restaurants/1/menu")
    assert r.status_code == 200
    assert "menu" in r.json()

def test_restaurant_menu_returns_404_for_missing_restaurant():
    """GET /restaurants/{id}/menu should return 404 when restaurant does not exist"""
    r = client.get("/restaurants/9999/menu")
    assert r.status_code == 404
    assert r.json()["detail"] == "Restaurant not found"

def test_visible_item_has_ok_status_and_display_price():
    """Visible item with valid price should have ok status and formatted display price"""
    r = client.get("/restaurants/1/menu")
    data = r.json()
    item = next(i for i in data["menu"] if i["is_visible"] and i["price_cents"] > 0)
    assert item["price_status"] == "ok"
    assert item["display_price"].startswith("$")
    assert len(item["display_price"]) > 1

def test_hidden_item_has_no_display_price():
    """Hidden item should return None display price"""
    r = client.get("/restaurants/1/menu")
    item = next((i for i in r.json()["menu"] if i["id"] == 2), None)
    assert item is not None
    assert item["display_price"] is None

def test_visible_negative_price_is_flagged():
    """Visible item with negative price should be flagged as invalid"""
    r = client.get("/restaurants/1/menu")
    item = next((i for i in r.json()["menu"] if i["id"] == 3), None)
    assert item is not None
    assert item["price_status"] == "invalid"
    assert item["display_price"] is None

def test_visible_missing_price_is_flagged():
    """Visible item with None price should be flagged as missing"""
    r = client.get("/restaurants/1/menu")
    item = next((i for i in r.json()["menu"] if i["id"] == 4), None)
    assert item is not None
    assert item["price_status"] == "missing"
    assert item["display_price"] is None

def _assert_all_items_belong_to(restaurant_id: int) -> None:
    """Assert every menu item in the response carries the correct restaurant_id"""
    r = client.get(f"/restaurants/{restaurant_id}/menu")
    assert r.status_code == 200
    for item in r.json()["menu"]:
        assert item["restaurant_id"] == restaurant_id, (
            f"Expected restaurant_id={restaurant_id}, got {item['restaurant_id']}"
        )

@pytest.mark.parametrize("restaurant_id", [1, 2])
def test_all_items_linked_to_correct_restaurant(restaurant_id):
    """All menu items in the response must carry the id of the restaurant they belong to"""
    _assert_all_items_belong_to(restaurant_id)
