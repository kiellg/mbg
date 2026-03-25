"""Tests for category and dietary tag validation in MenuItemCreate and category name"""
# pylint: disable=duplicate-code

from unittest.mock import patch
import copy
from pydantic import ValidationError
import pytest
from app.schemas.restaurant import MenuItemCreate
from app.services.restaurants_service import get_restaurant_menu

BASE_RECORD = {
    "id": 1,
    "name": "Test Bistro",
    "address": "123 Main St",
    "rating": 4,
    "opening_hours": "9am-9pm",
    "owner_id": "42",
    "menu": [],
}

SERVICE = "app.services.restaurants_service"

def make_item(**overrides):
    """Helper to create a menu item dict with default values and overrides"""
    base = {
        "id": 1,
        "restaurant_id": 1,
        "name": "Burger",
        "price_cents": 1299,
        "description": "",
        "dietary_tag": "vegan",
        "is_visible": True,
        "is_active": True,
        "is_available": True,
        "category": {"id": 1, "name": ""},
    }
    return {**base, **overrides}

def test_valid_category_id_accepted():
    """Test that a valid category_id is accepted and set correctly"""
    item = MenuItemCreate(
        name="Burger", price_cents=999, category_id=1,
    )
    assert item.category_id == 1

def test_invalid_category_id_rejected():
    """Test that an invalid category_id raises a ValidationError"""
    with pytest.raises(ValidationError) as exc:
        MenuItemCreate(name="Burger", price_cents=999, category_id=999)
    assert "Invalid category_id" in str(exc.value)

def test_valid_dietary_tag_accepted():
    """Test that a valid dietary_tag is accepted and normalized to lowercase"""
    item = MenuItemCreate(name="Salad", price_cents=500, category_id=1, dietary_tag="vegan")
    assert item.dietary_tag == "vegan"

def test_invalid_dietary_tag_rejected():
    """Test that an invalid dietary_tag raises a ValidationError"""
    with pytest.raises(ValidationError) as exc:
        MenuItemCreate(name="Salad", price_cents=500, category_id=1, dietary_tag="keto")
    assert "Invalid dietary_tag" in str(exc.value)

def test_menu_item_category_name_injected():
    """Test that get_restaurant_menu injects category name based on category id"""
    record = copy.deepcopy(BASE_RECORD)
    record["menu"] = [make_item(category={"id": 1, "name": ""})]
    with patch(f"{SERVICE}.get_restaurant_record", return_value=record):
        result = get_restaurant_menu(1)
    assert result.menu[0].category.name == "Appetizer"
