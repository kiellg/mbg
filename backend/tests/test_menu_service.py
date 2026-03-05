"""Tests for the menu service"""

import pytest
from fastapi import HTTPException
from backend.app.services.restaurants_service import (get_restaurant_menu,format_cad_from_cents)

def test_format_cad_from_cents():
    """Test the price formatting function"""
    assert format_cad_from_cents(1099) == "$10.99"
    assert format_cad_from_cents(0) == "$0.00"
    assert format_cad_from_cents(500) == "$5.00"

def test_service_raises_404_for_missing_restaurant():
    """Test that requesting a non-existent restaurant raises a 404 error"""
    with pytest.raises(HTTPException) as exc:
        get_restaurant_menu(999)
    assert exc.value.status_code == 404

def test_service_returns_valid_price_for_normal_item():
    """Test that a normal menu item returns a valid price and status"""
    restaurant = get_restaurant_menu(1)
    burger = next(i for i in restaurant.menu if i.id == 1)
    assert burger.price_status.value == "ok"
    assert burger.display_price == "$49.99"

def test_service_hides_price_for_hidden_item():
    """Test that hidden menu items do not have a display price"""
    restaurant = get_restaurant_menu(1)
    hidden = next(i for i in restaurant.menu if i.id == 2)
    assert hidden.display_price is None

def test_service_flags_invalid_price():
    """Test that visible items with negative price are flagged as invalid"""
    restaurant = get_restaurant_menu(1)
    invalid = next(i for i in restaurant.menu if i.id == 3)
    assert invalid.price_status.value == "invalid"
    assert invalid.display_price is None

def test_service_flags_missing_price():
    """Test that visible items with missing price are flagged as missing"""
    restaurant = get_restaurant_menu(1)
    missing = next(i for i in restaurant.menu if i.id == 4)
    assert missing.price_status.value == "missing"
    assert missing.display_price is None

def test_service_links_all_items_to_restaurant():
    """Test that all menu items have the correct restaurant_id set"""
    restaurant = get_restaurant_menu(1)
    for item in restaurant.menu:
        assert item.restaurant_id == 1

def test_service_does_not_mix_items_across_restaurants():
    """Test that items from restaurant 2 must not carry restaurant 1 id"""
    restaurant = get_restaurant_menu(2)
    for item in restaurant.menu:
        assert item.restaurant_id == 2
        assert item.restaurant_id != 1
