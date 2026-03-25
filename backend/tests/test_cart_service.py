# pylint: disable=unused-argument
"""Unit tests for the cart_service module."""
from datetime import datetime, timezone
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.services import cart_service
from app.repositories import cart_repo
from app.schemas.cart import CartItemCreate, CartItemUpdate

FAKE_MENU_ITEM = {"id": 1, "name": "Taco", "price_cents": 500, "is_available": True}
FAKE_UNAVAILABLE_ITEM = {"id": 2, "name": "Sushi", "price_cents": 1200, "is_available": False}


def test_add_item_creates_cart_and_returns_cart_response(monkeypatch):
    """Adding an item to a non-existent cart creates the cart and returns correct response."""
    restaurant_id = 1
    created_cart = {
        "id": 1, "customer_id": "42", "restaurant_id": restaurant_id,
        "created_at": datetime.now(timezone.utc).isoformat(), "items": []
    }

    monkeypatch.setattr(cart_repo, "get_cart_by_customer_and_restaurant", lambda cid, rid: None)
    monkeypatch.setattr(cart_repo, "create_cart", lambda cid, rid: created_cart)

    def fake_add_item_to_cart(cart_id, menu_item_id_arg, quantity):
        created_cart["items"].append({
            "id": 1, "cart_id": cart_id,
            "menu_item_id": menu_item_id_arg, "quantity": quantity
        })
        return created_cart["items"][-1]

    monkeypatch.setattr(cart_repo, "add_item_to_cart", fake_add_item_to_cart)
    monkeypatch.setattr(cart_repo, "get_cart_by_id", lambda cart_id: created_cart)

    with patch("app.services.cart_service.restaurant_repo") as mock_restaurant_repo:
        mock_restaurant_repo.get_restaurant_record.return_value = {"id": 1}
        mock_restaurant_repo.get_menu_item.return_value = FAKE_MENU_ITEM

        payload = CartItemCreate(menu_item_id=1, quantity=2)
        resp = cart_service.add_item("42", restaurant_id, payload)

    assert resp.id == created_cart["id"]
    assert resp.customer_id == "42"
    assert resp.restaurant_id == restaurant_id
    assert len(resp.items) == 1
    assert resp.cart_subtotal_cents == 500 * 2


def test_add_item_unavailable_raises(monkeypatch):
    """Adding an unavailable menu item should raise 400."""
    with patch("app.services.cart_service.restaurant_repo") as mock_restaurant_repo:
        mock_restaurant_repo.get_restaurant_record.return_value = {"id": 1}
        mock_restaurant_repo.get_menu_item.return_value = FAKE_UNAVAILABLE_ITEM

        payload = CartItemCreate(menu_item_id=2, quantity=1)
        with pytest.raises(HTTPException) as excinfo:
            cart_service.add_item("1", 1, payload)

    assert excinfo.value.status_code == 400


def test_update_item_cart_not_found_raises(monkeypatch):
    """Updating an item in a non-existent cart should raise 404."""
    monkeypatch.setattr(cart_repo, "get_cart_by_customer_and_restaurant", lambda cid, rid: None)

    payload = CartItemUpdate(quantity=3)
    with pytest.raises(HTTPException) as excinfo:
        cart_service.update_item(customer_id="1", restaurant_id=99, item_id=1, payload=payload)

    assert excinfo.value.status_code == 404

def test_update_item_returns_updated_cart(monkeypatch):
    """Should return updated CartResponse when item quantity is changed."""
    restaurant_id = 1
    cart = {
        "id": 1, "customer_id": "42", "restaurant_id": restaurant_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "items": [{"id": 1, "cart_id": 1, "menu_item_id": 1, "quantity": 3}]
    }
    monkeypatch.setattr(
        cart_repo, "get_cart_by_customer_and_restaurant", lambda cid, rid: cart
    )
    monkeypatch.setattr(
        cart_repo, "update_item_quantity",
        lambda cart_id, item_id, qty: {"id": 1, "quantity": qty}
    )
    monkeypatch.setattr(cart_repo, "get_cart_by_id", lambda cart_id: cart)

    with patch("app.services.cart_service.restaurant_repo") as mock_restaurant_repo:
        mock_restaurant_repo.get_restaurant_record.return_value = {"id": 1}
        mock_restaurant_repo.get_menu_item.return_value = FAKE_MENU_ITEM

        payload = CartItemUpdate(quantity=3)
        resp = cart_service.update_item("42", restaurant_id, 1, payload)

    assert resp.id == 1
    assert resp.items[0].quantity == 3

def test_update_item_raises_404_if_item_not_in_cart(monkeypatch):
    """Should raise 404 when item does not exist in the cart."""
    cart = {
        "id": 1, "customer_id": "42", "restaurant_id": 1,
        "created_at": datetime.now(timezone.utc).isoformat(), "items": []
    }
    monkeypatch.setattr(
        cart_repo, "get_cart_by_customer_and_restaurant", lambda cid, rid: cart
    )
    monkeypatch.setattr(
        cart_repo, "update_item_quantity", lambda cart_id, item_id, qty: None
    )

    with pytest.raises(HTTPException) as exc:
        cart_service.update_item("42", 1, 99, CartItemUpdate(quantity=2))
    assert exc.value.status_code == 404

def test_remove_item_not_found_raises(monkeypatch):
    """Removing an item that doesn't exist in the cart should raise 404."""
    cart = {
        "id": 5, "customer_id": "7", "restaurant_id": "1",
        "created_at": datetime.now(timezone.utc).isoformat(), "items": []
    }
    monkeypatch.setattr(cart_repo, "get_cart_by_customer_and_restaurant", lambda cid, rid: cart)
    monkeypatch.setattr(cart_repo, "remove_item_from_cart", lambda cart_id, item_id: False)

    with pytest.raises(HTTPException) as excinfo:
        cart_service.remove_item(customer_id="7", restaurant_id="1", item_id=1)

    assert excinfo.value.status_code == 404

def test_remove_item_cart_not_found_raises(monkeypatch):
    """Should raise 404 when cart does not exist."""
    monkeypatch.setattr(
        cart_repo, "get_cart_by_customer_and_restaurant", lambda cid, rid: None
    )

    with pytest.raises(HTTPException) as exc:
        cart_service.remove_item("42", 1, 1)
    assert exc.value.status_code == 404

def test_get_cart_returns_cart_response(monkeypatch):
    """Should return CartResponse when cart exists."""
    restaurant_id = 1
    cart = {
        "id": 1, "customer_id": "42", "restaurant_id": restaurant_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "items": [{"id": 1, "cart_id": 1, "menu_item_id": 1, "quantity": 2}]
    }
    monkeypatch.setattr(
        cart_repo, "get_cart_by_customer_and_restaurant", lambda cid, rid: cart
    )

    with patch("app.services.cart_service.restaurant_repo") as mock_restaurant_repo:
        mock_restaurant_repo.get_restaurant_record.return_value = {"id": 1}
        mock_restaurant_repo.get_menu_item.return_value = FAKE_MENU_ITEM

        resp = cart_service.get_cart("42", restaurant_id)

    assert resp.id == 1
    assert resp.customer_id == "42"
    assert resp.cart_subtotal_cents == 500 * 2

def test_get_cart_raises_404_if_not_found(monkeypatch):
    """Should raise 404 when cart does not exist."""
    monkeypatch.setattr(
        cart_repo, "get_cart_by_customer_and_restaurant", lambda cid, rid: None
    )

    with pytest.raises(HTTPException) as exc:
        cart_service.get_cart("42", 1)
    assert exc.value.status_code == 404
