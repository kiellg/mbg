"""Unit tests for notifications router."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies import get_current_user
from backend.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_auth():
    """Override auth dependency for all tests in this file."""
    app.dependency_overrides[get_current_user] = lambda: {"user_id": "user-123"}
    yield
    app.dependency_overrides.clear()


@patch("backend.app.routers.notifications.notification_service.list_notifications_for_user")
def test_read_notifications_returns_200_and_calls_service(mock_list_notifications):
    """GET /notifications should return the service payload for the current user."""
    mock_list_notifications.return_value = [
        {
            "message": "Order placed.",
            "timestamp": "2026-03-16T10:00:00+00:00",
            "order_id": "abc1234",
        }
    ]

    response = client.get("/notifications")

    assert response.status_code == 200
    assert response.json() == mock_list_notifications.return_value
    mock_list_notifications.assert_called_once_with("user-123")
