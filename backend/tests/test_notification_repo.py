"""Unit tests for notification_repo.py."""

from app.data.notification_data import NOTIFICATIONS
from app.repositories.notification_repo import create_notification, list_notification_records


def setup_function():
    """Reset notification state before each test."""
    NOTIFICATIONS.clear()


def test_list_notification_records_returns_newest_first():
    """Notifications should be returned in reverse insertion order."""
    NOTIFICATIONS.extend(
        [
            {
                "message": "First",
                "timestamp": "2026-03-16T10:00:00+00:00",
                "order_id": "1",
                "event_type": "order_placed",
                "audience_roles": ["customer"],
            },
            {
                "message": "Second",
                "timestamp": "2026-03-16T10:05:00+00:00",
                "order_id": "2",
                "event_type": "order_status_changed",
                "audience_roles": ["customer", "manager"],
            },
            {
                "message": "Third",
                "timestamp": "2026-03-16T10:10:00+00:00",
                "order_id": "3",
                "event_type": "driver_assigned",
                "audience_roles": ["driver"],
            },
        ]
    )

    result = list_notification_records()

    assert [record["order_id"] for record in result] == ["3", "2", "1"]


def test_create_notification_stores_event_type_and_audience_roles():
    """Created notifications should persist audience metadata for filtering."""
    result = create_notification(
        "Order placed.",
        "order-123",
        "order_placed",
        ["customer"],
    )

    assert result["event_type"] == "order_placed"
    assert result["audience_roles"] == ["customer"]
    assert NOTIFICATIONS[0]["event_type"] == "order_placed"
    assert NOTIFICATIONS[0]["audience_roles"] == ["customer"]
