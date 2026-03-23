"""Integration tests for delivery router endpoints"""
# pylint: disable=duplicate-code, unused-argument, unused-import, ungrouped-imports
from unittest.mock import patch
import copy
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from backend.main import app
from backend.app.data.order_data import _ORDERDB as ORDER_DB
from backend.app.schemas.order import OrderStatus

client = TestClient(app)

ROUTER = "backend.app.routers.deliveries"

ORDER_ID = "abc1234"
DRIVER_ID = "driver-123"
DRIVER_HEADERS = {"session-token": "valid-driver-token"}

FAKE_ORDER = {
    "order_id": ORDER_ID,
    "status": OrderStatus.PENDING,
    "delivery_time": "30 mins",
    "delivery_time_actual": 28.5,
    "delivery_delay": 1.5,
    "driver_name": "John Doe",
    "delivery_method": "bike",
    "delivery_distance": 3.5,
    "route_taken": "Main St -> Oak Ave",
    "restaurant_id": 1,
    "customer_id": "cust-001",
    "delivery_address": "123 Test St",
    "items": [],
    "subtotal": "0.00",
    "tax": "0.00",
    "delivery_fee": "0.00",
    "total": "0.00",
}

_ORIGINAL_DB = copy.deepcopy(ORDER_DB)

def setup_function():
    """Reset all in-memory state before each test"""
    ORDER_DB.clear()
    ORDER_DB.update(copy.deepcopy(_ORIGINAL_DB))
    ORDER_DB[ORDER_ID] = copy.deepcopy(FAKE_ORDER)

def _override_order(order_id: str, overrides: dict) -> None:
    """Mutate ORDER_DB to apply overrides to a specific order"""
    ORDER_DB[order_id] = {**ORDER_DB[order_id], **overrides}

def _as_driver():
    """Patch require_driver at the router level"""
    return patch(f"{ROUTER}.require_driver",
                 return_value={"user_id": DRIVER_ID, "role": "driver"})

def test_get_delivery_status_returns_200():
    """GET /{order_id}/status should return 200 with correct status and ETA fields"""
    response = client.get(f"/orders/{ORDER_ID}/status")

    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == ORDER_ID
    assert data["status"] == "Pending"
    assert data["delivery_time"] == "30 mins"
    assert data["delivery_time_actual"] == 28.5
    assert data["delivery_delay"] == 1.5

def test_get_delivery_status_not_found():
    """GET /{order_id}/status should return 404 for a non-existent order — fault injection"""
    response = client.get("/orders/nonexistent/status")
    assert response.status_code == 404

@pytest.mark.parametrize("status", [
    OrderStatus.PENDING, 
    OrderStatus.COOKING, 
    OrderStatus.OUT_FOR_DELIVERY, 
    OrderStatus.DELIVERED
    ])
def test_get_delivery_status_reflects_status(status):
    """GET /{order_id}/status should reflect whatever status the order currently has"""
    _override_order(ORDER_ID, {"status": status})
    response = client.get(f"/orders/{ORDER_ID}/status")

    assert response.status_code == 200
    assert response.json()["status"] == status

def test_get_delivery_details_returns_200():
    """GET /{order_id}/details should return 200 with driver and method fields"""
    response = client.get(f"/orders/{ORDER_ID}/details")

    assert response.status_code == 200
    data = response.json()
    assert data["driver_name"] == "John Doe"
    assert data["delivery_method"] == "bike"
    assert data["delivery_distance"] == 3.5

def test_get_delivery_details_not_found():
    """GET /{order_id}/details should return 404 for a non-existent order — fault injection"""
    response = client.get("/orders/nonexistent/details")
    assert response.status_code == 404


@patch("backend.app.routers.deliveries.delivery_service.assign_driver_to_order")
@patch("backend.app.routers.deliveries.require_manager")
def test_manager_assign_driver_returns_200(mock_require_manager, mock_assign_driver):
    """PATCH /{order_id}/driver should assign the driver for a manager."""
    mock_require_manager.return_value = {"user_id": "manager-123"}
    mock_assign_driver.return_value = {
        "order_id": "abc1234",
        "driver_id": "driver-123",
        "driver_name": "John Doe",
    }

    response = client.patch(
        "/orders/abc1234/driver",
        json={"driver_id": "driver-123"},
        headers={"session-token": "valid-manager-token"},
    )

    assert response.status_code == 200
    assert response.json()["driver_id"] == "driver-123"
    mock_assign_driver.assert_called_once_with(
        order_id="abc1234",
        driver_id="driver-123",
        manager_id="manager-123",
    )


@patch("backend.app.routers.deliveries.require_manager")
def test_assign_driver_returns_403_if_not_manager(mock_require_manager):
    """PATCH /{order_id}/driver should return 403 for non-managers."""
    mock_require_manager.side_effect = HTTPException(status_code=403, detail="Access denied")

    response = client.patch(
        "/orders/abc1234/driver",
        json={"driver_id": "driver-123"},
    )

    assert response.status_code == 403


def test_driver_update_status_valid_transition():
    """Driver should be able to update status through a valid transition"""
    with _as_driver():
        response = client.patch(
            f"/orders/{ORDER_ID}/status",
            json={"status": "Cooking"},
            headers=DRIVER_HEADERS,
        )

    assert response.status_code == 200
    assert response.json()["status"] == "Cooking"


def test_driver_update_status_no_token():
    """PATCH /{order_id}/status should return 403 with no valid driver token — exception handling"""
    with _as_driver() as mock_driver:
        mock_driver.side_effect = HTTPException(status_code=403, detail="Forbidden")
        response = client.patch(
            f"/orders/{ORDER_ID}/status",
            json={"status": "Cooking"},
        )

    assert response.status_code == 403


def test_driver_update_status_order_not_found():
    """PATCH /{order_id}/status should return 404 if order does not exist — fault injection"""
    with _as_driver():
        response = client.patch(
            "/orders/nonexistent/status",
            json={"status": "Cooking"},
            headers=DRIVER_HEADERS,
        )

    assert response.status_code == 404


@pytest.mark.parametrize("current_status, attempted_status", [
    (OrderStatus.PENDING, OrderStatus.PENDING),
    (OrderStatus.CANCELLED, OrderStatus.COOKING),
    (OrderStatus.DELIVERED, OrderStatus.COOKING),
])
def test_driver_invalid_status_transition(current_status, attempted_status):
    """PATCH /{order_id}/status should reject invalid status transitions — fault injection"""
    _override_order(ORDER_ID, {"status": current_status})

    with _as_driver():
        response = client.patch(
            f"/orders/{ORDER_ID}/status",
            json={"status": attempted_status},
            headers=DRIVER_HEADERS,
        )

    assert response.status_code == 400

@patch("backend.app.services.delivery_service.order_repo")
@patch("backend.app.services.delivery_service.restaurant_repo")
@patch("backend.app.routers.deliveries.require_manager")
def test_get_kitchen_queue_returns_200(mock_require_manager,
                                       mock_restaurant_repo,
                                       mock_order_repo):
    """GET /orders/kitchen/{restaurant_id} should return 200 for a valid manager."""
    mock_require_manager.return_value = {"user_id": "josemou"}
    mock_restaurant_repo.get_restaurant_record.return_value = {"id": 1, "owner_id": "josemou"}
    mock_order_repo.list_order_records.return_value = []

    response = client.get("/orders/kitchen/1",
                          headers={"session-token": "valid-manager-token"},
                          )
    assert response.status_code == 200

@patch("backend.app.routers.deliveries.require_manager")
def test_get_kitchen_queue_raises_403_if_not_manager(mock_require_manager):
    """GET /orders/kitchen/{restaurant_id} should return 403 for non-managers."""
    mock_require_manager.side_effect = HTTPException(status_code=403, detail="Access denied")
    response = client.get("/orders/kitchen/1")
    assert response.status_code == 403
