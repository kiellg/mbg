# pylint: disable=unused-argument, duplicate-code
"""Unit tests for the pending order router endpoint."""

from decimal import Decimal
from unittest.mock import patch
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.dependencies import get_current_user
from app.schemas.order import DeliveryMethod, OrderResponse, OrderStatus
from main import app

CUSTOMER_ID = "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"

FAKE_ORDER_RESPONSE = OrderResponse(
    order_id="abc1234",
    created_at=datetime.now(timezone.utc),
    customer_id=CUSTOMER_ID,
    restaurant_id=1,
    status=OrderStatus.PENDING,
    delivery_address="123 Test St",
    delivery_method=DeliveryMethod.WALK,
    items=[],
    subtotal=Decimal("22.50"),
    tax=Decimal("2.25"),
    delivery_fee=Decimal("5.00"),
    total=Decimal("29.75"),
)

client = TestClient(app)


def override_get_current_user():
    """Override auth to return a fixed user for tests."""
    return {"user_id": CUSTOMER_ID}


@patch("app.routers.orders.order_service.update_pending_order")
def test_update_pending_order_returns_200_and_calls_service(mock_update):
    """Test that PATCH /orders/{order_id} updates a pending order."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    mock_update.return_value = FAKE_ORDER_RESPONSE

    response = client.patch(
        "/orders/abc1234",
        json={
            "items": [{"menu_item_id": 1, "quantity": 2}],
            "delivery_method": "walk",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["order_id"] == "abc1234"
    assert response.json()["total"] == "29.75"

    payload = mock_update.call_args.kwargs["payload"]
    assert payload.items[0].menu_item_id == 1
    assert payload.items[0].quantity == 2
    mock_update.assert_called_once_with(
        order_id="abc1234",
        user_id=CUSTOMER_ID,
        payload=payload,
    )
