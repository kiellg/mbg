"""Tests for the menu service"""

import pytest
from fastapi import HTTPException
from backend.app.services.restaurants_service import (get_restaurant_menu,format_cad_from_cents)

def test_format_cad_from_cents():
    assert format_cad_from_cents(1099) == "$10.99"
    assert format_cad_from_cents(0) == "$0.00"
    assert format_cad_from_cents(500) == "$5.00"

def test_service_raises_404_for_missing_restaurant():
    with pytest.raises(HTTPException) as exc:
        get_restaurant_menu(999)
    assert exc.value.status_code == 404

def test_service_returns_valid_price_for_normal_item():
    restaurant = get_restaurant_menu(1)
    burger = next(i for i in restaurant.menu if i.id == 1)
    assert burger.price_status.value == "ok"
    assert burger.display_price == "$49.99"

def test_service_hides_price_for_hidden_item():
    restaurant = get_restaurant_menu(1)
    hidden = next(i for i in restaurant.menu if i.id == 2)
    assert hidden.display_price is None

def test_service_flags_invalid_price():
    restaurant = get_restaurant_menu(1)
    invalid = next(i for i in restaurant.menu if i.id == 3)
    assert invalid.price_status.value == "invalid"
    assert invalid.display_price is None

def test_service_flags_missing_price():
    restaurant = get_restaurant_menu(1)
    missing = next(i for i in restaurant.menu if i.id == 4)
    assert missing.price_status.value == "missing"
    assert missing.display_price is None
