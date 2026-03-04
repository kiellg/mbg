# backend/tests/test_cart_data.py

import pytest
from app.data.cart_data import _CartDB
from datetime import datetime

def setup_function():
    """Clear _CartDB before each test to ensure a clean state."""
    _CartDB.clear()


def test_carts_starts_empty():
    assert _CartDB == {}


def test_cart_record_shape():
    """Manually insert a cart record and verify it matches the expected shape."""
    mock_cart = {
        "id": 1,
        "customer_id": 42,
        "restaurant_id": 3,
        "created_at": datetime.utcnow().isoformat(),
        "items": [
            {
                "id": 1,
                "menu_item_id": 7,
                "quantity": 2
            }
        ]
    }

    _CartDB[1] = mock_cart

    # Assert cart exists
    assert 1 in _CartDB

    # Assert top-level fields exist
    cart = _CartDB[1]
    assert "id" in cart
    assert "customer_id" in cart
    assert "restaurant_id" in cart
    assert "created_at" in cart
    assert "items" in cart

    # Assert correct values
    assert cart["id"] == 1
    assert cart["customer_id"] == 42
    assert cart["restaurant_id"] == 3

    # Assert items is a list
    assert isinstance(cart["items"], list)
    assert len(cart["items"]) == 1

    # Assert cart item shape
    item = cart["items"][0]
    assert "id" in item
    assert "menu_item_id" in item
    assert "quantity" in item

    # Assert cart item values
    assert item["id"] == 1
    assert item["menu_item_id"] == 7
    assert item["quantity"] == 2


def test_multiple_carts_stored_independently():
    """Verify multiple carts can coexist without overwriting each other."""
    _CartDB[1] = {"id": 1, "customer_id": 10, "restaurant_id": 1, "created_at": datetime.utcnow().isoformat(), "items": [{"id": 1, "menu_item_id": 7,"quantity": 2}]}
    _CartDB[2] = {"id": 2, "customer_id": 20, "restaurant_id": 2, "created_at": datetime.utcnow().isoformat(), "items": [{"id": 1, "menu_item_id": 7,"quantity": 2}]}

    assert len(_CartDB) == 2
    assert _CartDB[1]["customer_id"] == 10
    assert _CartDB[2]["customer_id"] == 20
