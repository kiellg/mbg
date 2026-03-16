"""Unit tests for notification_service.py."""

from backend.app.data.notification_data import NOTIFICATIONS
from backend.app.services import notification_service


def setup_function():
    """Reset notification state before each test."""
    NOTIFICATIONS.clear()


def test_create_order_placed_notification_stores_minimal_record():
    """Order placement notifications should store message, timestamp, and order_id."""
    record = notification_service.create_order_placed_notification("abc1234")

    assert record["message"] == "Order placed."
    assert record["order_id"] == "abc1234"
    assert "timestamp" in record
    assert NOTIFICATIONS == [record]


def test_create_order_status_changed_notification_stores_minimal_record():
    """Status change notifications should store message, timestamp, and order_id."""
    record = notification_service.create_order_status_changed_notification(
        "abc1234",
        "Cooking",
    )

    assert record["message"] == "Order status changed to Cooking."
    assert record["order_id"] == "abc1234"
    assert "timestamp" in record
    assert NOTIFICATIONS == [record]
