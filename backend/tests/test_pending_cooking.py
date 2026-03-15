"""Integration tests for PATCH /orders/{order_id}/status/cooking"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_mark_cooking_returns_200(mock_get_session, mock_get_role):
    """PATCH /status/cooking should return 200 when order is Pending"""
    mock_get_session.return_value = {"user_id": "manager-123"}
    mock_get_role.return_value = "manager"

    fake_order = {"order_id": "abc1234", "status": "Pending"}

    with patch("backend.app.data.order_data._ORDERDB", {"abc1234": fake_order}):
        response = client.patch(
            "/orders/abc1234/status/cooking",
            headers={"session-token": "valid-manager-token"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "Cooking"

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_mark_cooking_returns_400_when_not_pending(mock_get_session, mock_get_role):
    """PATCH /status/cooking should return 400 if order is not Pending"""
    mock_get_session.return_value = {"user_id": "manager-123"}
    mock_get_role.return_value = "manager"

    fake_order = {"order_id": "abc1234", "status": "Cooking"}

    with patch("backend.app.data.order_data._ORDERDB", {"abc1234": fake_order}):
        response = client.patch(
            "/orders/abc1234/status/cooking",
            headers={"session-token": "valid-manager-token"},
        )

    assert response.status_code == 400
    assert "Cannot transition" in response.json()["detail"]

@patch("backend.app.services.role_service.get_user_role")
@patch("backend.app.services.role_service.get_current_user_session")
def test_mark_cooking_returns_404_when_order_not_found(mock_get_session, mock_get_role):
    """PATCH /status/cooking should return 404 if order doesn't exist"""
    mock_get_session.return_value = {"user_id": "manager-123"}
    mock_get_role.return_value = "manager"

    with patch("backend.app.data.order_data._ORDERDB", {}):
        response = client.patch(
            "/orders/fake-id/status/cooking",
            headers={"session-token": "valid-manager-token"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
