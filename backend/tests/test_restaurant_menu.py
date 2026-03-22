"""Tests for the restaurant menu endpoint"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from backend.main import app

#pylint: disable=duplicate-code
FAKE_RESTAURANT = {
    "id": 1,
    "name": "Test Restaurant",
    "address": "123 Test St",
    "rating": 4,
    "opening_hours": "Mon-Sun 9-5",
   "menu": [
        {"id": 1, "name": "Burger",
         "price_cents": 4999,
         "is_visible": True,
         "is_active": True,
         "description": "",
         "dietary_tag": "",
         "is_available": True,
         "category": None},
        {"id": 2, "name": "Hidden Item",
         "price_cents": 999,  "is_visible":
         False, "is_active": True,
         "description": "",
         "dietary_tag": "",
         "is_available": True,
         "category": None},
        {"id": 3, "name": "Invalid Price",
         "price_cents": -100, "is_visible": True,
         "is_active": True,
         "description": "",
         "dietary_tag": "",
         "is_available": True,
         "category": None},
        {"id": 4,
         "name": "Missing Price",
         "price_cents": None,
         "is_visible": True,
         "is_active": True,
         "description": "",
         "dietary_tag": "",
         "is_available": True,
         "category": None},
    ],
}

_REPO = "backend.app.services.restaurants_service.get_restaurant_record"

client = TestClient(app)

def _get_menu_item(data: dict, item_id: int) -> dict:
    """Extract a menu item by id with a clear failure message"""
    item = next((i for i in data["menu"] if i["id"] == item_id), None)
    assert item is not None, f"Expected item with id={item_id} in menu"
    return item

def _get_menu(restaurant_id: int = 1) -> dict:
    """Perform GET /restaurants/{id}/menu and return parsed JSON"""
    r = client.get(f"/restaurants/{restaurant_id}/menu")
    return r

def test_restaurant_menu_returns_200():
    """GET /restaurants/{id}/menu should return 200 with menu data"""
    r = client.get("/restaurants/1/menu")
    assert r.status_code == 200
    assert "menu" in r.json()

@patch(_REPO)
def test_restaurant_menu_returns_404_for_missing_restaurant(mock_get_record):
    """GET /restaurants/{id}/menu should return 404 when restaurant does not exist"""
    mock_get_record.return_value = None
    r = _get_menu(999)
    assert r.status_code == 404
    assert r.json()["detail"] == "Restaurant not found"

@patch(_REPO)
def test_visible_item_has_ok_status_and_display_price(mock_get_record):
    """Visible item with valid price should have ok status and formatted display price"""
    mock_get_record.return_value = FAKE_RESTAURANT
    item = _get_menu_item(_get_menu().json(), 1)
    assert item["price_status"] == "ok"
    assert item["display_price"].startswith("$")
    assert len(item["display_price"]) > 1

@patch(_REPO)
def test_hidden_item_has_no_display_price(mock_get_record):
    """Hidden item should return None display price"""
    mock_get_record.return_value = FAKE_RESTAURANT
    item = _get_menu_item(_get_menu().json(), 2)
    assert item["display_price"] is None

@patch(_REPO)
def test_visible_negative_price_is_flagged(mock_get_record):
    """Visible item with negative price should be flagged as invalid fault injection"""
    mock_get_record.return_value = FAKE_RESTAURANT
    item = _get_menu_item(_get_menu().json(), 3)
    assert item["price_status"] == "invalid"
    assert item["display_price"] is None

@patch(_REPO)
def test_visible_missing_price_is_flagged(mock_get_record):
    """Visible item with missing price should be flagged as missing fault injection"""
    mock_get_record.return_value = FAKE_RESTAURANT
    item = _get_menu_item(_get_menu().json(), 4)
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
