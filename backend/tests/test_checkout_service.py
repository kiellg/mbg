# pylint: disable=unused-argument
"""Unit tests for checkout_service.py with mocked dependencies."""

from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from backend.app.data import cart_data
from backend.app.repositories import cart_repo, restaurant_repo, user_repo
from backend.app.schemas.order import DeliveryMethod, OrderStatus
from backend.app.services import checkout_service

CUSTOMER_ID = "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"

FAKE_CART = {
    "id": 1,
    "customer_id": CUSTOMER_ID,
    "restaurant_id": 1,
    "checked_out": False,
    "items": [
        {"menu_item_id": 1, "quantity": 2},
    ],
    "delivery_address": "123 Test St",
}

FAKE_ORDER_RESPONSE_DICT = {
    "order_id": "abc1234",
    "customer_id": CUSTOMER_ID,
    "restaurant_id": 1,
    "status": OrderStatus.PENDING,
    "delivery_address": "123 Test St",
    "delivery_method": DeliveryMethod.WALK,
    "items": [],
    "subtotal": Decimal("0.00"),
    "tax": Decimal("0.00"),
    "delivery_fee": Decimal("0.00"),
    "total": Decimal("0.00"),
}


def setup_function():
    """Reset shared state before each test."""
    cart_data._CARTDB.clear()
    cart_data.NEXT_CART_ID = 1
    cart_data.NEXT_ITEM_ID = 1
    user_repo.reset_users()
    restaurant_repo.reset_restaurants()


# for successful checkout
@patch("backend.app.services.checkout_service.restaurant_repo")
@patch("backend.app.services.checkout_service.user_repo")
@patch("backend.app.services.checkout_service.cart_repo")
@patch("backend.app.services.checkout_service.order_service")
def test_checkout_creates_order_and_marks_cart(mock_order_service,
                                               mock_cart_repo,
                                               mock_user_repo,
                                               mock_restaurant_repo):
    """Test that checkout creates an order and marks the cart as checked out."""
    mock_restaurant_repo.get_menu_item.return_value = {
        "id": 1,
        "is_available": True,
        "price_cents": 1000,
    }
    mock_user_repo.get_customer_by_user_id.return_value = {"user_id": CUSTOMER_ID,
                                                           "delivery_address": "123 Test St"}
    mock_cart_repo.get_cart_by_id.return_value = FAKE_CART
    mock_order_service.create_order.return_value = FAKE_ORDER_RESPONSE_DICT

    checkout_service.checkout(
        cart_id=1,
        customer_id=CUSTOMER_ID,
        delivery_method=DeliveryMethod.WALK,
    )

    mock_order_service.create_order.assert_called_once()
    mock_cart_repo.mark_cart_checked_out.assert_called_once_with(1)

@patch("backend.app.services.checkout_service.restaurant_repo")
@patch("backend.app.services.checkout_service.user_repo")
@patch("backend.app.services.checkout_service.cart_repo")
@patch("backend.app.services.checkout_service.order_service")
def test_checkout_uses_official_menu_price_for_order_items(mock_order_service,
                                                           mock_cart_repo,
                                                           mock_user_repo,
                                                           mock_restaurant_repo):
    """Test that checkout uses backend menu pricing for order items."""
    mock_cart_repo.get_cart_by_id.return_value = FAKE_CART
    mock_order_service.create_order.return_value = FAKE_ORDER_RESPONSE_DICT
    mock_user_repo.get_customer_by_user_id.return_value = {"user_id": CUSTOMER_ID,
                                                           "delivery_address": "123 Test St"}
    mock_restaurant_repo.get_menu_item.return_value = {
        "id": 1,
        "is_available": True,
        "price_cents": 2599,
    }

    checkout_service.checkout(
        cart_id=1,
        customer_id=CUSTOMER_ID,
        delivery_method=DeliveryMethod.WALK,
    )

    call_args = mock_order_service.create_order.call_args[0][0]
    assert call_args.items[0].item_price == Decimal("25.99")
    assert call_args.items[0].quantity == 2


@patch("backend.app.services.checkout_service.order_service")
def test_checkout_does_not_require_unit_price_cents_on_cart_items(mock_order_service):
    """Test that checkout works with the raw cart repo item shape."""
    user = user_repo.create_user("cust", "cust@test.com", "pw123")
    user_repo.create_customer(user["user_id"], "123 Test St")

    cart = cart_repo.create_cart(user["user_id"], 1)
    cart_repo.add_item_to_cart(cart["id"], 1, 2)

    mock_order_service.create_order.return_value = FAKE_ORDER_RESPONSE_DICT

    checkout_service.checkout(
        cart_id=cart["id"],
        customer_id=user["user_id"],
        delivery_method=DeliveryMethod.WALK,
    )

    stored_cart = cart_repo.get_cart_by_id(cart["id"])
    call_args = mock_order_service.create_order.call_args[0][0]

    assert "unit_price_cents" not in stored_cart["items"][0]
    assert call_args.items[0].item_price == Decimal("49.99")
    assert stored_cart["checked_out"] is True


# for cart not found
@patch("backend.app.services.checkout_service.cart_repo")
def test_checkout_raises_404_if_cart_not_found(mock_cart_repo):
    """Test that checkout raises 404 when the cart does not exist."""
    mock_cart_repo.get_cart_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        checkout_service.checkout(
            cart_id=99,
            customer_id=CUSTOMER_ID,
            delivery_method=DeliveryMethod.WALK,
        )

    assert exc.value.status_code == 404


# for wrong customer
@patch("backend.app.services.checkout_service.cart_repo")
def test_checkout_raises_403_if_wrong_customer(mock_cart_repo):
    """Test that checkout raises 403 when the cart belongs to a different customer."""
    mock_cart_repo.get_cart_by_id.return_value = FAKE_CART

    with pytest.raises(HTTPException) as exc:
        checkout_service.checkout(
            cart_id=1,
            customer_id="different-customer-id",
            delivery_method=DeliveryMethod.WALK,
        )

    assert exc.value.status_code == 403


# for already checked out
@patch("backend.app.services.checkout_service.cart_repo")
def test_checkout_raises_400_if_already_checked_out(mock_cart_repo):
    """Test that checkout raises 400 when the cart has already been checked out."""
    mock_cart_repo.get_cart_by_id.return_value = {**FAKE_CART, "checked_out": True}

    with pytest.raises(HTTPException) as exc:
        checkout_service.checkout(
            cart_id=1,
            customer_id=CUSTOMER_ID,
            delivery_method=DeliveryMethod.WALK,
        )

    assert exc.value.status_code == 400


# for empty cart
@patch("backend.app.services.checkout_service.cart_repo")
def test_checkout_raises_400_if_cart_is_empty(mock_cart_repo):
    """Test that checkout raises 400 when the cart has no items."""
    mock_cart_repo.get_cart_by_id.return_value = {**FAKE_CART, "items": []}

    with pytest.raises(HTTPException) as exc:
        checkout_service.checkout(
            cart_id=1,
            customer_id=CUSTOMER_ID,
            delivery_method=DeliveryMethod.WALK,
        )

    assert exc.value.status_code == 400
