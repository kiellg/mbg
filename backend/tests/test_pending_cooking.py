"""Integration tests for PATCH /orders/{order_id}/status/cancelled"""
# pylint: disable=duplicate-code

from unittest.mock import patch
import copy
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.data.order_data import _ORDERDB
from backend.app.schemas.order import OrderStatus

client = TestClient(app)

ROLE_SERVICE = "backend.app.services.role_service"

ORDER_ID        = "abc1234"
MANAGER_ID      = "manager-123"
MANAGER_HEADERS = {"session-token": "valid-manager-token"}

FAKE_ORDER = {
    "order_id": ORDER_ID,
    "status": OrderStatus.COOKING,
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
    "total": "25.99",
}

_ORIGINAL_ORDERDB = copy.deepcopy(_ORDERDB)

def setup_function():  # pylint: disable=duplicate-code
    """Reset all in-memory state before each test"""
    _ORDERDB.clear()
    _ORDERDB.update(copy.deepcopy(_ORIGINAL_ORDERDB))
    _ORDERDB[ORDER_ID] = copy.deepcopy(FAKE_ORDER)

def _override_order(order_id: str, overrides: dict) -> None:
    """Mutate _ORDERDB to apply overrides to a specific order"""
    _ORDERDB[order_id] = {**_ORDERDB.get(order_id, copy.deepcopy(FAKE_ORDER)), **overrides}

def _as_manager():
    """Patch role_service auth layer to simulate a valid manager session"""
    return (
        patch(f"{ROLE_SERVICE}.get_current_user_session",
              return_value={"user_id": MANAGER_ID}),
        patch(f"{ROLE_SERVICE}.get_user_role", return_value="manager"),
    )

def test_mark_cancelled_returns_200():
    """PATCH /status/cancelled should return 200 when order is Cooking"""
    with _as_manager()[0], _as_manager()[1]:
        response = client.patch(
            f"/orders/{ORDER_ID}/status/cancelled",
            headers=MANAGER_HEADERS,
        )

    assert response.status_code == 200
    assert response.json()["status"] == "Cancelled"
    assert "25.99" in response.json()["message"]

@pytest.mark.parametrize("invalid_status", [
    OrderStatus.PENDING,
    OrderStatus.DELIVERED,
    OrderStatus.OUT_FOR_DELIVERY,
])
def test_mark_cancelled_returns_400_when_not_cooking(invalid_status):
    """PATCH /status/cancelled should return 400 if order is not Cooking"""
    _override_order(ORDER_ID, {"status": invalid_status})

    with _as_manager()[0], _as_manager()[1]:
        response = client.patch(
            f"/orders/{ORDER_ID}/status/cancelled",
            headers=MANAGER_HEADERS,
        )

    assert response.status_code == 400
    assert "Cannot transition" in response.json()["detail"]

def test_mark_cancelled_returns_404_when_order_not_found():
    """PATCH /status/cancelled should return 404 if order does not exist"""
    with _as_manager()[0], _as_manager()[1]:
        response = client.patch(
            "/orders/fake-id/status/cancelled",
            headers=MANAGER_HEADERS,
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
