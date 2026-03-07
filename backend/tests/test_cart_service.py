# pylint: disable=global-statement,unused-argument
"""Unit tests for the cart_service module, covering key functionalities and edge cases."""
from datetime import datetime, timezone
import copy
import pytest
from fastapi import HTTPException
from backend.app.services import cart_service as cart_service
from backend.app.repositories import cart_repo
from backend.app.schemas.cart import CartItemCreate, CartItemUpdate

_ORIG_DB = None

def setup_function():
    """Clear the restaurant database before each test to ensure isolation."""
    global _ORIG_DB
    _ORIG_DB = copy.deepcopy(cart_service.RESTAURANT_DB)
    cart_service.RESTAURANT_DB.clear()

def teardown_function():
    """Restore the original restaurant database after each test."""
    cart_service.RESTAURANT_DB.clear()
    if _ORIG_DB is not None:
        cart_service.RESTAURANT_DB.update(_ORIG_DB)

def test_add_item_creates_cart_and_returns_cart_response(monkeypatch):
    """Test that adding an item to a non-existent cart
    creates the cart and returns the correct response."""
    restaurant_id = 1
    menu_item_id = 7
    cart_service.RESTAURANT_DB[restaurant_id] = {
        "id": restaurant_id,
        "menu": [{"id": menu_item_id, "name": "Taco", "price_cents": 500, "is_available": True}]
    }

    created_cart = {"id": 1, "customer_id": 42, "restaurant_id": restaurant_id,
                    "created_at": datetime.now(timezone.utc).isoformat(), "items": []}

    monkeypatch.setattr(cart_repo, "get_cart_by_customer_and_restaurant", lambda cid, rid: None)
    monkeypatch.setattr(cart_repo, "create_cart", lambda cid, rid: created_cart)

    def fake_add_item_to_cart(cart_id, menu_item_id_arg, quantity):
        created_cart["items"].append({
            "id": 1,
            "cart_id": cart_id,
            "menu_item_id": menu_item_id_arg,
            "quantity": quantity
        })
        return created_cart["items"][-1]

    monkeypatch.setattr(cart_repo, "add_item_to_cart", fake_add_item_to_cart)

    payload = CartItemCreate(menu_item_id=menu_item_id, quantity=2)
    resp = cart_service.add_item(42, restaurant_id, payload)

    assert resp.id == created_cart["id"]
    assert resp.customer_id == 42
    assert resp.restaurant_id == restaurant_id
    assert len(resp.items) == 1
    assert resp.total_cents == 500 * 2


def test_add_item_unavailable_raises(monkeypatch):
    """Test that trying to add an unavailable menu item raises an HTTPException."""
    restaurant_id = 2
    menu_item_id = 9
    cart_service.RESTAURANT_DB[restaurant_id] = {
        "id": restaurant_id,
        "menu": [{"id": menu_item_id, "name": "Sushi", "price_cents": 1200, "is_available": False}]
    }

    payload = CartItemCreate(menu_item_id=menu_item_id, quantity=1)

    with pytest.raises(HTTPException) as excinfo:
        cart_service.add_item(1, restaurant_id, payload)
    assert excinfo.value.status_code == 400


def test_update_item_cart_not_found_raises(monkeypatch):
    """Test that updating an item in a non-existent cart raises an HTTPException."""
    monkeypatch.setattr(cart_repo, "get_cart_by_id", lambda cart_id: None)

    payload = CartItemUpdate(quantity=3)
    with pytest.raises(HTTPException) as excinfo:
        cart_service.update_item(customer_id=1, cart_id=99, item_id=1, payload=payload)
    assert excinfo.value.status_code == 404


def test_remove_item_not_found_raises(monkeypatch):
    """Test that trying to remove an item that doesn't exist in the cart raises an HTTPException."""
    cart = {"id": 5, "customer_id": 7, "restaurant_id": 1,
            "created_at": datetime.now(timezone.utc).isoformat(), "items": []}
    monkeypatch.setattr(cart_repo, "get_cart_by_id", lambda cart_id: cart)
    monkeypatch.setattr(cart_repo, "remove_item_from_cart", lambda cart_id, item_id: False)

    with pytest.raises(HTTPException) as excinfo:
        cart_service.remove_item(customer_id=7, cart_id=5, item_id=1)
    assert excinfo.value.status_code == 404
