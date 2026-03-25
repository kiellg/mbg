"""Tests for restaurant data layer schema validation"""

import pytest
from pydantic import ValidationError
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantUpdate,
    MenuItemCreate,
    MenuItemUpdate,
)

def test_restaurant_create_valid():
    """Valid restaurant create should pass"""
    r = RestaurantCreate(name="Sushi World", address="123 Sushi St")
    assert r.name == "Sushi World"
    assert r.address == "123 Sushi St"
    assert r.opening_hours == ""

def test_restaurant_create_rejects_empty_name():
    """Empty name should raise validation error"""
    with pytest.raises(ValidationError):
        RestaurantCreate(name="", address="123 Sushi St")

def test_restaurant_update_all_optional():
    """RestaurantUpdate with no fields should be valid"""
    update = RestaurantUpdate()
    assert update.name is None
    assert update.address is None
    assert update.rating is None
    assert update.opening_hours is None

def test_restaurant_update_rejects_empty_name():
    """Empty name in update should raise validation error"""
    with pytest.raises(ValidationError):
        RestaurantUpdate(name="")

def test_menu_item_create_valid():
    """Valid menu item create should pass"""
    item = MenuItemCreate(name="Burger", price_cents=1000, category_id=1)
    assert item.name == "Burger"
    assert item.price_cents == 1000
    assert item.description == ""
    assert item.is_visible is True

def test_menu_item_create_rejects_empty_name():
    """Empty name should raise validation error"""
    with pytest.raises(ValidationError):
        MenuItemCreate(name="", price_cents=1000, category_id=1)

def test_menu_item_create_defaults():
    """Default values should be set correctly"""
    item = MenuItemCreate(name="Burger", price_cents=500, category_id=1)
    assert item.dietary_tag == ""
    assert item.is_active is True
    assert item.is_available is True

def test_menu_item_update_all_optional():
    """MenuItemUpdate with no fields should be valid"""
    update = MenuItemUpdate()
    assert update.name is None
    assert update.price_cents is None
    assert update.category_id is None

def test_menu_item_update_rejects_empty_name():
    """Empty name in update should raise validation error"""
    with pytest.raises(ValidationError):
        MenuItemUpdate(name="")
