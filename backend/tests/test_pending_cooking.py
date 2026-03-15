"""Integration tests for PATCH /orders/{order_id}/status/cancelled"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_mark_cancelled_returns_200(mock_get_session, mock_get_role):
    """PATCH /status/cancelled should return 200 when order is Cooking"""
    mock_get_session.return_value = {"user_id": "manager-123"}
    mock_get_role.return_value = "manager"

    fake_order = {"order_id": "abc1234", "status": "Cooking", "total": 25.99}

    with patch("backend.app.data.order_data._ORDERDB", {"abc1234": fake_order}):
        response = client.patch(
            "/orders/abc1234/status/cancelled",
            headers={"session-token": "valid-manager-token"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "Cancelled"
    assert "25.99" in response.json()["message"]

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_mark_cancelled_returns_400_when_not_cooking(mock_get_session, mock_get_role):
    """PATCH /status/cancelled should return 400 if order is not Cooking"""
    mock_get_session.return_value = {"user_id": "manager-123"}
    mock_get_role.return_value = "manager"

    fake_order = {"order_id": "abc1234", "status": "Pending"}

    with patch("backend.app.data.order_data._ORDERDB", {"abc1234": fake_order}):
        response = client.patch(
            "/orders/abc1234/status/cancelled",
            headers={"session-token": "valid-manager-token"},
        )

    assert response.status_code == 400
    assert "Cannot transition" in response.json()["detail"]

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_mark_cancelled_returns_404_when_order_not_found(mock_get_session, mock_get_role):
    """PATCH /status/cancelled should return 404 if order doesn't exist"""
    mock_get_session.return_value = {"user_id": "manager-123"}
    mock_get_role.return_value = "manager"

    with patch("backend.app.data.order_data._ORDERDB", {}):
        response = client.patch(
            "/orders/fake-id/status/cancelled",
            headers={"session-token": "valid-manager-token"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
