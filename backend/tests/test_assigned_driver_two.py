"""Integration tests for GET /orders/assigned endpoint"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

FAKE_ASSIGNED_ORDER = {
    "order_id": "abc1234",
    "delivery_address": "123 Test St",
    "customer_phone": "250-555-0100",
    "driver_name": "Driver 1",
    "driver_id": "driver-123",
    "delivery_method": "bike",
    "status": "Out for Delivery",
    "delivery_time": "30 mins",
}

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_get_assigned_deliveries_returns_200(
    mock_get_session, mock_get_role
):
    """GET /assigned should return 200 with list of assigned orders for the driver"""
    mock_get_session.return_value = {"user_id": "driver-123"}
    mock_get_role.return_value = "driver"

    with patch("backend.app.data.order_data._ORDERDB", {"abc1234": FAKE_ASSIGNED_ORDER}):
        response = client.get(
            "/orders/assigned",
            headers={"session-token": "valid-driver-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["order_id"] == "abc1234"
    assert data[0]["customer_address"] == "123 Test St"
    assert data[0]["customer_phone"] == "250-555-0100"
    assert data[0]["driver_name"] == "Driver 1"
    assert data[0]["status"] == "Out for Delivery"

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_get_assigned_deliveries_returns_empty_list_when_no_assignments(
    mock_get_session, mock_get_role
):
    """GET /assigned should return empty list when driver has no assigned orders"""
    mock_get_session.return_value = {"user_id": "driver-123"}
    mock_get_role.return_value = "driver"

    with patch("backend.app.data.order_data._ORDERDB", {}):
        response = client.get(
            "/orders/assigned",
            headers={"session-token": "valid-driver-token"},
        )

    assert response.status_code == 200
    assert response.json() == []

def test_get_assigned_deliveries_returns_401_when_no_token():
    """GET /assigned should return 401 when no session token is provided"""
    response = client.get("/orders/assigned")

    assert response.status_code == 401
    assert response.json()["detail"] == "Login required"

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_get_assigned_deliveries_returns_403_for_non_driver(mock_get_session, mock_get_role):
    """GET /assigned should return 403 when user is not a driver"""
    mock_get_session.return_value = {"user_id": "customer-123"}
    mock_get_role.return_value = "customer"

    response = client.get(
        "/orders/assigned",
        headers={"session-token": "customer-token"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"
