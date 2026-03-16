"""Integration tests for PATCH /orders/{order_id}/status/out-for-delivery and /delivered"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_mark_out_for_delivery_returns_200(mock_get_session, mock_get_role):
    """PATCH /status/out-for-delivery should return 200 when order is Cooking"""
    mock_get_session.return_value = {"user_id": "driver-123"}
    mock_get_role.return_value = "driver"

    fake_order = {"order_id": "abc1234", "status": "Cooking"}

    with patch("backend.app.data.order_data._ORDERDB", {"abc1234": fake_order}):
        response = client.patch(
            "/orders/abc1234/status/out-for-delivery",
            headers={"session-token": "valid-driver-token"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "Out for Delivery"

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_mark_out_for_delivery_returns_400_when_not_cooking(mock_get_session, mock_get_role):
    """PATCH /status/out-for-delivery should return 400 if order is not Cooking"""
    mock_get_session.return_value = {"user_id": "driver-123"}
    mock_get_role.return_value = "driver"

    fake_order = {"order_id": "abc1234", "status": "Pending"}

    with patch("backend.app.data.order_data._ORDERDB", {"abc1234": fake_order}):
        response = client.patch(
            "/orders/abc1234/status/out-for-delivery",
            headers={"session-token": "valid-driver-token"},
        )

    assert response.status_code == 400
    assert "Cannot transition" in response.json()["detail"]

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_mark_out_for_delivery_returns_404_when_order_not_found(mock_get_session, mock_get_role):
    """PATCH /status/out-for-delivery should return 404 if order doesn't exist"""
    mock_get_session.return_value = {"user_id": "driver-123"}
    mock_get_role.return_value = "driver"

    with patch("backend.app.data.order_data._ORDERDB", {}):
        response = client.patch(
            "/orders/fake-id/status/out-for-delivery",
            headers={"session-token": "valid-driver-token"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_mark_delivered_returns_200(mock_get_session, mock_get_role):
    """PATCH /status/delivered should return 200 when order is Out for Delivery"""
    mock_get_session.return_value = {"user_id": "driver-123"}
    mock_get_role.return_value = "driver"

    fake_order = {"order_id": "abc1234", "status": "Out for Delivery"}

    with patch("backend.app.data.order_data._ORDERDB", {"abc1234": fake_order}):
        response = client.patch(
            "/orders/abc1234/status/delivered",
            headers={"session-token": "valid-driver-token"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "Delivered"


@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_mark_delivered_returns_400_when_not_out_for_delivery(mock_get_session, mock_get_role):
    """PATCH /status/delivered should return 400 if order is not Out for Delivery"""
    mock_get_session.return_value = {"user_id": "driver-123"}
    mock_get_role.return_value = "driver"

    fake_order = {"order_id": "abc1234", "status": "Cooking"}

    with patch("backend.app.data.order_data._ORDERDB", {"abc1234": fake_order}):
        response = client.patch(
            "/orders/abc1234/status/delivered",
            headers={"session-token": "valid-driver-token"},
        )

    assert response.status_code == 400
    assert "Cannot transition" in response.json()["detail"]

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_mark_delivered_returns_404_when_order_not_found(mock_get_session, mock_get_role):
    """PATCH /status/delivered should return 404 if order doesn't exist"""
    mock_get_session.return_value = {"user_id": "driver-123"}
    mock_get_role.return_value = "driver"

    with patch("backend.app.data.order_data._ORDERDB", {}):
        response = client.patch(
            "/orders/fake-id/status/delivered",
            headers={"session-token": "valid-driver-token"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
