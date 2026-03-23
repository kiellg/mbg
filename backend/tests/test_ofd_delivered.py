"""Integration tests for PATCH /orders/{order_id}/status/out-for-delivery and /delivered"""

from unittest.mock import patch
import copy
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.data.order_data import _ORDERDB
from backend.app.schemas.order import OrderStatus

client = TestClient(app)

ROLE_SERVICE = "backend.app.services.role_service"

ORDER_ID = "abc1234"
DRIVER_ID = "driver-123"
DRIVER_HEADERS = {"session-token": "valid-driver-token"}

_ORIGINAL_ORDERDB = copy.deepcopy(_ORDERDB)

FAKE_ORDER = {
    "order_id": ORDER_ID,
    "status": OrderStatus.PENDING,
    "delivery_time": "",
    "delivery_time_actual": 0.0,
    "delivery_delay": 0.0,
    "driver_name": "",
    "delivery_method": "bike",
    "delivery_distance": 0.0,
    "route_taken": "",
    "restaurant_id": 1,
    "customer_id": "cust-001",
    "delivery_address": "123 Test St",
    "items": [],
    "subtotal": "0.00",
    "tax": "0.00",
    "delivery_fee": "0.00",
    "total": "0.00",
}

def setup_function():  # pylint: disable=duplicate-code
    """Reset all in-memory state before each test"""
    _ORDERDB.clear()
    _ORDERDB.update(copy.deepcopy(_ORIGINAL_ORDERDB))
    _ORDERDB[ORDER_ID] = copy.deepcopy(FAKE_ORDER)

def _override_order(order_id: str, overrides: dict) -> None:
    """Mutate _ORDERDB to apply overrides to a specific order"""
    _ORDERDB[order_id] = {**_ORDERDB.get(order_id, copy.deepcopy(FAKE_ORDER)), **overrides}

def _as_driver():
    """Patch role_service auth layer to simulate a valid driver session"""
    return (
        patch(f"{ROLE_SERVICE}.get_current_user_session",
              return_value={"user_id": DRIVER_ID}),
        patch(f"{ROLE_SERVICE}.get_user_role", return_value="driver"),
    )

def test_mark_out_for_delivery_returns_200():
    """PATCH /status/out-for-delivery should return 200 when order is Cooking"""
    _override_order(ORDER_ID, {"status": "Cooking"})

    with _as_driver()[0], _as_driver()[1]:
        response = client.patch(
            f"/orders/{ORDER_ID}/status/out-for-delivery",
            headers=DRIVER_HEADERS,
        )

    assert response.status_code == 200
    assert response.json()["status"] == "Out for Delivery"

@pytest.mark.parametrize("invalid_status", [OrderStatus.PENDING, OrderStatus.DELIVERED, OrderStatus.CANCELLED])
def test_mark_out_for_delivery_returns_400_when_not_cooking(invalid_status):
    """PATCH /status/out-for-delivery should return 400 if order is not Cooking"""
    _override_order(ORDER_ID, {"status": invalid_status})

    with _as_driver()[0], _as_driver()[1]:
        response = client.patch(
            f"/orders/{ORDER_ID}/status/out-for-delivery",
            headers=DRIVER_HEADERS,
        )

    assert response.status_code == 400
    assert "Cannot transition" in response.json()["detail"]

def test_mark_out_for_delivery_returns_404_when_order_not_found():
    """PATCH /status/out-for-delivery should return 404 if order does not exist — fault injection"""
    with _as_driver()[0], _as_driver()[1]:
        response = client.patch(
            "/orders/fake-id/status/out-for-delivery",
            headers=DRIVER_HEADERS,
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

def test_mark_delivered_returns_200():
    """PATCH /status/delivered should return 200 when order is Out for Delivery"""
    _override_order(ORDER_ID, {"status": "Out for Delivery"})

    with _as_driver()[0], _as_driver()[1]:
        response = client.patch(
            f"/orders/{ORDER_ID}/status/delivered",
            headers=DRIVER_HEADERS,
        )

    assert response.status_code == 200
    assert response.json()["status"] == "Delivered"

@pytest.mark.parametrize("invalid_status", [OrderStatus.PENDING, OrderStatus.COOKING, OrderStatus.CANCELLED])
def test_mark_delivered_returns_400_when_not_out_for_delivery(invalid_status):
    """PATCH /status/delivered should return 400 if order is not Out for Delivery"""
    _override_order(ORDER_ID, {"status": invalid_status})

    with _as_driver()[0], _as_driver()[1]:
        response = client.patch(
            f"/orders/{ORDER_ID}/status/delivered",
            headers=DRIVER_HEADERS,
        )

    assert response.status_code == 400
    assert "Cannot transition" in response.json()["detail"]

def test_mark_delivered_returns_404_when_order_not_found():
    """PATCH /status/delivered should return 404 if order does not exist — fault injection"""
    with _as_driver()[0], _as_driver()[1]:
        response = client.patch(
            "/orders/fake-id/status/delivered",
            headers=DRIVER_HEADERS,
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
