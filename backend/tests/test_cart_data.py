"""Unit tests for cart_data simulated database structure."""

from datetime import datetime
import backend.app.data.cart_data as cart_data

def setup_function():
    """Clear _CARTDB before each test to ensure a clean state."""
    cart_data._CARTDB.clear()
    cart_data.NEXT_CART_ID = 1
    cart_data.NEXT_ITEM_ID = 1

def test_carts_starts_empty():
    """Ensure the cart database starts empty."""
    assert not cart_data._CARTDB

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

    cart_data._CARTDB[1] = mock_cart

    assert 1 in cart_data._CARTDB

    cart = cart_data._CARTDB[1]
    assert "id" in cart
    assert "customer_id" in cart
    assert "restaurant_id" in cart
    assert "created_at" in cart
    assert "items" in cart

    assert cart["id"] == 1
    assert cart["customer_id"] == 42
    assert cart["restaurant_id"] == 3

    assert isinstance(cart["items"], list)
    assert len(cart["items"]) == 1

    item = cart["items"][0]
    assert "id" in item
    assert "menu_item_id" in item
    assert "quantity" in item

    assert item["id"] == 1
    assert item["menu_item_id"] == 7
    assert item["quantity"] == 2


def test_multiple_carts_stored_independently():
    """Verify multiple carts can coexist without overwriting each other."""
    cart_data._CARTDB[1] = {
        "id": 1, 
        "customer_id": 10, 
        "restaurant_id": 1, 
        "created_at": datetime.utcnow().isoformat(), 
        "items": [{"id": 1, "menu_item_id": 7,"quantity": 2}]}
    cart_data._CARTDB[2] = {
        "id": 2, 
        "customer_id": 20, 
        "restaurant_id": 2, 
        "created_at": datetime.utcnow().isoformat(), 
        "items": [{"id": 1, "menu_item_id": 7,"quantity": 2}]
    }

    assert len(cart_data._CARTDB) == 2
    assert cart_data._CARTDB[1]["customer_id"] == 10
    assert cart_data._CARTDB[2]["customer_id"] == 20
