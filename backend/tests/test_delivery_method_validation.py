"""Tests for PATCH /orders/{order_id}/driver with delivery method validation"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app

client = TestClient(app)

ROLE_SERVICE = "app.services.role_service"
DELIVERY_SERVICE = "app.routers.deliveries"

ORDER_ID = "abc1234"
MANAGER_ID = "manager-123"
DRIVER_ID = "driver-123"
MANAGER_HEADERS = {"session-token": "valid-manager-token"}

FAKE_ASSIGN_RESULT = {
    "order_id": ORDER_ID,
    "driver_id": DRIVER_ID,
    "driver_name": "John Doe",
    "delivery_method": "bike",
}


def _as_manager():
    """Patch role_service auth layer to simulate a valid manager session"""
    return (
        patch(f"{ROLE_SERVICE}.get_current_user_session",
              return_value={"user_id": MANAGER_ID}),
        patch(f"{ROLE_SERVICE}.get_user_role", return_value="manager"),
    )

def test_assign_driver_matching_method_returns_200():
    """PATCH /driver should return 200 when driver method matches order method"""
    with _as_manager()[0], _as_manager()[1], \
         patch(f"{DELIVERY_SERVICE}.delivery_service.assign_driver_to_order",
               return_value=FAKE_ASSIGN_RESULT) as mock_assign:
        response = client.patch(
            f"/orders/{ORDER_ID}/driver",
            json={"driver_id": DRIVER_ID, "delivery_method": "bike"},
            headers=MANAGER_HEADERS,
        )
    assert response.status_code == 200
    assert response.json()["driver_id"] == DRIVER_ID
    assert response.json()["delivery_method"] == "bike"
    mock_assign.assert_called_once_with(
        order_id=ORDER_ID,
        driver_id=DRIVER_ID,
        manager_id=MANAGER_ID,
        delivery_method="bike",
    )

def test_assign_driver_missing_delivery_method_returns_400():
    """PATCH /driver should return 400 when delivery_method is missing"""
    with _as_manager()[0], _as_manager()[1]:
        response = client.patch(
            f"/orders/{ORDER_ID}/driver",
            json={"driver_id": DRIVER_ID},
            headers=MANAGER_HEADERS,
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing delivery_method"

def test_assign_driver_method_mismatch_returns_400():
    """PATCH /driver should return 400 when driver method does not match order method"""
    with _as_manager()[0], _as_manager()[1], \
         patch(f"{DELIVERY_SERVICE}.delivery_service.assign_driver_to_order",
               side_effect=HTTPException(
                    status_code=400, 
                    detail="Driver's delivery method 'walk' does not match the requested method 'bike'.")):
        response = client.patch(
            f"/orders/{ORDER_ID}/driver",
            json={"driver_id": DRIVER_ID, "delivery_method": "bike"},
            headers=MANAGER_HEADERS,
        )
    assert response.status_code == 400
    assert "does not match" in response.json()["detail"]

@pytest.mark.parametrize("method", ["bike", "walk", "car"])
def test_assign_driver_valid_delivery_methods(method):
    """PATCH /driver should accept all valid delivery methods when they match"""
    fake_result = {**FAKE_ASSIGN_RESULT, "delivery_method": method}
    with _as_manager()[0], _as_manager()[1], \
         patch(f"{DELIVERY_SERVICE}.delivery_service.assign_driver_to_order",
               return_value=fake_result):
        response = client.patch(
            f"/orders/{ORDER_ID}/driver",
            json={"driver_id": DRIVER_ID, "delivery_method": method},
            headers=MANAGER_HEADERS,
        )
    assert response.status_code == 200
    assert response.json()["delivery_method"] == method
    