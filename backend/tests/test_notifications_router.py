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
            "notification_id": "notif-123",
            "message": "Order placed.",
            "timestamp": "2026-03-16T10:00:00+00:00",
            "order_id": "abc1234",
            "is_read": False,
        }
    ]

    response = client.get("/notifications")

    assert response.status_code == 200
    assert response.json() == mock_list_notifications.return_value
    mock_list_notifications.assert_called_once_with("user-123")


@patch("backend.app.routers.notifications.notification_service.mark_notification_as_read_for_user")
def test_mark_notification_as_read_returns_200_and_calls_service(mock_mark_notification):
    """PATCH /notifications/{notification_id}/read should mark the notification as read."""
    mock_mark_notification.return_value = {
        "notification_id": "notif-123",
        "message": "Order placed.",
        "timestamp": "2026-03-16T10:00:00+00:00",
        "order_id": "abc1234",
        "is_read": True,
    }

    response = client.patch("/notifications/notif-123/read")

    assert response.status_code == 200
    assert response.json() == mock_mark_notification.return_value
    mock_mark_notification.assert_called_once_with("notif-123", "user-123")
