"""Unit tests for notification_repo.py."""

from backend.app.data.notification_data import NOTIFICATIONS
from backend.app.repositories.notification_repo import list_notification_records


def setup_function():
    """Reset notification state before each test."""
    NOTIFICATIONS.clear()


def test_list_notification_records_returns_newest_first():
    """Notifications should be returned in reverse insertion order."""
    NOTIFICATIONS.extend(
        [
            {"message": "First", "timestamp": "2026-03-16T10:00:00+00:00", "order_id": "1"},
            {"message": "Second", "timestamp": "2026-03-16T10:05:00+00:00", "order_id": "2"},
            {"message": "Third", "timestamp": "2026-03-16T10:10:00+00:00", "order_id": "3"},
        ]
    )

    result = list_notification_records()

    assert [record["order_id"] for record in result] == ["3", "2", "1"]
