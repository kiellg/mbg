# pylint: disable=unused-argument, unused-import
"""Unit tests for checkout_router.py with mocked service and auth."""

from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app
from app.schemas.order import DeliveryMethod, OrderStatus, OrderResponse
from app.dependencies import get_current_user

CUSTOMER_ID = "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"

FAKE_ORDER_RESPONSE = OrderResponse(
    order_id="abc1234",
    customer_id=CUSTOMER_ID,
    restaurant_id=1,
    status=OrderStatus.PENDING,
    delivery_address="123 Test St",
    delivery_method=DeliveryMethod.WALK,
    items=[],
    subtotal=Decimal("0.00"),
    tax=Decimal("0.00"),
    delivery_fee=Decimal("0.00"),
    total=Decimal("0.00"),
)

client = TestClient(app)
def override_get_current_user():
    """Override for get_current_user dependency to return a fixed user_id.
    Only for testing purposes. Because dependency does not work with patch."""
    return {"user_id": CUSTOMER_ID}

@patch("app.routers.checkouts.checkout_service.checkout")
@patch("app.dependencies.get_current_user", return_value={"user_id": CUSTOMER_ID})
def test_checkout_returns_201_and_order(mock_user, mock_checkout):
    """Test that POST /checkout/{cart_id} returns 201 and the created order."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    mock_checkout.return_value = FAKE_ORDER_RESPONSE

    response = client.post(
        "/checkout/1",
        json={"delivery_method": "walk"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    assert response.json()["order_id"] == "abc1234"
    assert response.json()["status"] == "Pending"


@patch("app.routers.checkouts.checkout_service.checkout")
@patch("app.dependencies.get_current_user", return_value={"user_id": CUSTOMER_ID})
def test_checkout_passes_correct_args_to_service(mock_user, mock_checkout):
    """Test that the router passes cart_id, customer_id, and delivery_method to the service."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    mock_checkout.return_value = FAKE_ORDER_RESPONSE

    client.post("/checkout/1", json={"delivery_method": "walk"})

    app.dependency_overrides.clear()
    mock_checkout.assert_called_once_with(
        cart_id=1,
        customer_id=CUSTOMER_ID,
        delivery_method=DeliveryMethod.WALK,
    )


@patch("app.routers.checkouts.checkout_service.checkout")
@patch("app.dependencies.get_current_user", return_value={"user_id": CUSTOMER_ID})
def test_checkout_ignores_extra_pricing_fields_in_request(mock_user, mock_checkout):
    """Test that extra pricing fields do not affect the checkout request."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    mock_checkout.return_value = FAKE_ORDER_RESPONSE

    response = client.post(
        "/checkout/1",
        json={
            "delivery_method": "walk",
            "subtotal": "0.01",
            "total": "0.02",
            "item_price": "0.03",
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    mock_checkout.assert_called_once_with(
        cart_id=1,
        customer_id=CUSTOMER_ID,
        delivery_method=DeliveryMethod.WALK,
    )


@patch("app.routers.checkouts.checkout_service.checkout")
@patch("app.dependencies.get_current_user", return_value={"user_id": CUSTOMER_ID})
def test_checkout_raises_404_if_cart_not_found(mock_user, mock_checkout):
    """Test that 404 from the service propagates through the router."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    mock_checkout.side_effect = HTTPException(status_code=404, detail="Cart 99 not found")

    response = client.post("/checkout/99", json={"delivery_method": "walk"})

    app.dependency_overrides.clear()
    assert response.status_code == 404


@patch("app.routers.checkouts.checkout_service.checkout")
@patch("app.dependencies.get_current_user", return_value={"user_id": CUSTOMER_ID})
def test_checkout_raises_403_if_wrong_customer(mock_user, mock_checkout):
    """Test that 403 from the service propagates through the router."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    mock_checkout.side_effect = HTTPException(
        status_code=403, detail="Not authorized to checkout this cart"
    )

    response = client.post("/checkout/1", json={"delivery_method": "walk"})

    app.dependency_overrides.clear()
    assert response.status_code == 403


@patch("app.routers.checkouts.checkout_service.checkout")
@patch("app.dependencies.get_current_user", return_value={"user_id": CUSTOMER_ID})
def test_checkout_raises_400_if_already_checked_out(mock_user, mock_checkout):
    """Test that 400 from the service propagates through the router."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    mock_checkout.side_effect = HTTPException(
        status_code=400, detail="Cart has already been checked out"
    )

    response = client.post("/checkout/1", json={"delivery_method": "walk"})

    app.dependency_overrides.clear()
    assert response.status_code == 400
