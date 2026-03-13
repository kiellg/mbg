# pylint: disable=unused-argument
"""Unit tests for checkout_service.py with mocked dependencies."""

from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from backend.app.schemas.order import DeliveryMethod, OrderStatus
from backend.app.services import checkout_service

CUSTOMER_ID = "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"

FAKE_CART = {
    "id": 1,
    "customer_id": CUSTOMER_ID,
    "restaurant_id": 1,
    "checked_out": False,
    "items": [
        {"quantity": 2, "unit_price_cents": 1000},
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


# for successful checkout
@patch("backend.app.services.checkout_service.user_repo")
@patch("backend.app.services.checkout_service.cart_repo")
@patch("backend.app.services.checkout_service.order_service")
def test_checkout_creates_order_and_marks_cart(mock_order_service, mock_cart_repo, mock_user_repo):
    """Test that checkout creates an order and marks the cart as checked out."""
    mock_user_repo.get_customer_by_user_id.return_value = {"user_id": CUSTOMER_ID, "delivery_address": "123 Test St"}
    mock_cart_repo.get_cart_by_id.return_value = FAKE_CART
    mock_order_service.create_order.return_value = FAKE_ORDER_RESPONSE_DICT

    checkout_service.checkout(
        cart_id=1,
        customer_id=CUSTOMER_ID,
        delivery_method=DeliveryMethod.WALK,
    )

    mock_order_service.create_order.assert_called_once()
    mock_cart_repo.mark_cart_checked_out.assert_called_once_with(1)

@patch("backend.app.services.checkout_service.user_repo")
@patch("backend.app.services.checkout_service.cart_repo")
@patch("backend.app.services.checkout_service.order_service")
def test_checkout_converts_price_cents_to_decimal(mock_order_service, mock_cart_repo, mock_user_repo):
    """Test that price_cents are correctly converted to Decimal item_price."""
    mock_cart_repo.get_cart_by_id.return_value = FAKE_CART
    mock_order_service.create_order.return_value = FAKE_ORDER_RESPONSE_DICT
    mock_user_repo.get_customer_by_user_id.return_value = {"user_id": CUSTOMER_ID, "delivery_address": "123 Test St"}

    checkout_service.checkout(
        cart_id=1,
        customer_id=CUSTOMER_ID,
        delivery_method=DeliveryMethod.WALK,
    )

    call_args = mock_order_service.create_order.call_args[0][0]
    assert call_args.items[0].item_price == Decimal("10.00")
    assert call_args.items[0].quantity == 2


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