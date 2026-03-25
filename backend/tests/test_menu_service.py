"""Tests for the menu service"""

from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.services.restaurants_service import (
    get_restaurant_menu,
    format_cad_from_cents)

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

_REPO = "app.services.restaurants_service.get_restaurant_record"

def _make_restaurant_with(menu_index: int) -> dict:
    """Return a fake restaurant containing only the menu item at the given index"""
    return {**FAKE_RESTAURANT, "menu": [FAKE_RESTAURANT["menu"][menu_index].copy()]}

@pytest.mark.parametrize("cents, expected", [
    (1099, "$10.99"),
    (0,    "$0.00"),
    (500,  "$5.00"),
])
def test_format_cad_from_cents(cents, expected):
    """Test that format_cad_from_cents correctly formats various cent values"""
    assert format_cad_from_cents(cents) == expected

@patch(_REPO)
def test_service_raises_404_for_missing_restaurant(mock_get_restaurant_record):
    """Test that requesting a non-existent restaurant raises a 404 error"""
    mock_get_restaurant_record.return_value = None
    with pytest.raises(HTTPException) as exc:
        get_restaurant_menu(999)
    assert exc.value.status_code == 404

@patch(_REPO)
def test_service_returns_valid_price_for_normal_item(mock_get_restaurant_record):
    """Test that a normal menu item returns a valid price and status"""
    mock_get_restaurant_record.return_value = _make_restaurant_with(0)
    restaurant = get_restaurant_menu(1)
    burger = next(i for i in restaurant.menu if i.id == 1)
    assert burger.price_status.value == "ok"
    assert burger.display_price == "$49.99"

@patch(_REPO)
def test_service_hides_price_for_hidden_item(mock_get_restaurant_record):
    """Test that hidden menu items do not have a display price"""
    mock_get_restaurant_record.return_value = _make_restaurant_with(1)
    restaurant = get_restaurant_menu(1)
    hidden = next(i for i in restaurant.menu if i.id == 2)
    assert hidden.display_price is None

@patch(_REPO)
def test_service_flags_invalid_price(mock_get_restaurant_record):
    """Test that visible items with negative price are flagged as invalid"""
    mock_get_restaurant_record.return_value = _make_restaurant_with(2)
    restaurant = get_restaurant_menu(1)
    invalid = next(i for i in restaurant.menu if i.id == 3)
    assert invalid.price_status.value == "invalid"
    assert invalid.display_price is None

@patch(_REPO)
def test_service_flags_missing_price(mock_get_restaurant_record):
    """Test that visible items with missing price are flagged as missing"""
    mock_get_restaurant_record.return_value = _make_restaurant_with(3)
    restaurant = get_restaurant_menu(1)
    missing = next(i for i in restaurant.menu if i.id == 4)
    assert missing.price_status.value == "missing"
    assert missing.display_price is None

def _assert_all_items_belong_to(restaurant_id: int) -> None:
    """Assert every menu item carries the correct restaurant_id"""
    restaurant = get_restaurant_menu(restaurant_id)
    for item in restaurant.menu:
        assert item.restaurant_id == restaurant_id, (
            f"Expected restaurant_id={restaurant_id}, got {item.restaurant_id}"
        )

@pytest.mark.parametrize("restaurant_id", [1, 2])
def test_service_links_all_items_to_correct_restaurant(restaurant_id):
    """All menu items must carry the id of the restaurant they belong to"""
    _assert_all_items_belong_to(restaurant_id)
