"""Unit tests for notification_service.py."""
# pylint: disable=protected-access

from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.services import notification_service

ORDER_ID = "order-123"
USER_ID = "user-123"


def test_create_order_placed_notification_calls_create_notification_with_expected_message():
    """Order placed helper should pass the expected message to the repo layer."""
    record = {
        "notification_id": "notif-123",
        "message": "Order placed.",
        "timestamp": "2026-03-16T10:00:00+00:00",
        "order_id": ORDER_ID,
        "read_by_user_ids": [],
    }

    with patch(
        "app.services.notification_service.create_notification",
        return_value=record,
    ) as mock_create_notification:
        result = notification_service.create_order_placed_notification(ORDER_ID)

    assert result == record
    mock_create_notification.assert_called_once_with("Order placed.", ORDER_ID)


def test_create_order_status_changed_notification_formats_status_message():
    """Status change helper should format the status into the notification message."""
    record = {
        "notification_id": "notif-123",
        "message": "Order status changed to Cooking.",
        "timestamp": "2026-03-16T10:00:00+00:00",
        "order_id": ORDER_ID,
        "read_by_user_ids": [],
    }

    with patch(
        "app.services.notification_service.create_notification",
        return_value=record,
    ) as mock_create_notification:
        result = notification_service.create_order_status_changed_notification(
            ORDER_ID,
            "Cooking",
        )

    assert result == record
    mock_create_notification.assert_called_once_with(
        "Order status changed to Cooking.",
        ORDER_ID,
    )


def test_create_driver_assigned_notification_calls_create_notification_with_expected_message():
    """Driver assignment helper should pass the expected message to the repo layer."""
    record = {
        "notification_id": "notif-123",
        "message": "You have been assigned a delivery.",
        "timestamp": "2026-03-16T10:00:00+00:00",
        "order_id": ORDER_ID,
        "read_by_user_ids": [],
    }

    with patch(
        "app.services.notification_service.create_notification",
        return_value=record,
    ) as mock_create_notification:
        result = notification_service.create_driver_assigned_notification(ORDER_ID)

    assert result == record
    mock_create_notification.assert_called_once_with(
        "You have been assigned a delivery.",
        ORDER_ID,
    )


@patch("app.services.notification_service.logger")
@patch("app.services.notification_service.create_notification")
def test_create_notification_safely_logs_failure_and_returns_empty_dict(
    mock_create_notification,
    mock_logger,
):
    """Notification creation failures should be logged and suppressed."""
    mock_create_notification.side_effect = RuntimeError("notification write failed")

    result = notification_service._create_notification_safely(
        "Order placed.",
        ORDER_ID,
        notification_service.NotificationEventType.ORDER_PLACED,
    )

    assert not result
    mock_logger.exception.assert_called_once()
    log_args = mock_logger.exception.call_args[0]
    assert log_args[0] == (
        "Notification creation failed. event_type=%s order_id=%s timestamp=%s error=%s"
    )
    assert log_args[1] == "order_placed"
    assert log_args[2] == ORDER_ID
    assert isinstance(log_args[3], str)
    assert log_args[4] == "notification write failed"


def test_notification_is_visible_to_user_returns_true_for_customer_order():
    """Customers should see notifications for their own orders."""
    order = {"customer_id": USER_ID, "restaurant_id": 1}

    result = notification_service._notification_is_visible_to_user(order, USER_ID, "customer")

    assert result is True


@patch("app.services.notification_service.get_restaurant_record")
def test_notification_is_visible_to_user_returns_true_for_restaurant_owner(
    mock_get_restaurant_record,
):
    """Managers should see notifications for restaurants they own."""
    mock_get_restaurant_record.return_value = {"id": 1, "owner_id": USER_ID}
    order = {"customer_id": "other-user", "restaurant_id": 1}

    result = notification_service._notification_is_visible_to_user(order, USER_ID, "manager")

    assert result is True
    mock_get_restaurant_record.assert_called_once_with(1)


def test_notification_is_visible_to_user_returns_true_for_assigned_driver():
    """Drivers should see notifications for orders assigned to them."""
    order = {"customer_id": "other-user", "restaurant_id": 1, "driver_id": USER_ID}

    result = notification_service._notification_is_visible_to_user(order, USER_ID, "driver")

    assert result is True


def test_notification_is_visible_to_user_returns_false_for_unknown_role():
    """Unknown roles should never be able to view notifications."""
    order = {"customer_id": USER_ID, "restaurant_id": 1, "driver_id": USER_ID}

    result = notification_service._notification_is_visible_to_user(order, USER_ID, "guest")

    assert result is False


def test_build_notification_response_marks_notification_read_for_current_user():
    """Response building should derive the read flag from read_by_user_ids."""
    record = {
        "notification_id": "notif-123",
        "message": "Order placed.",
        "timestamp": "2026-03-16T10:00:00+00:00",
        "order_id": ORDER_ID,
        "read_by_user_ids": [USER_ID],
    }

    result = notification_service._build_notification_response(record, USER_ID)

    assert result.notification_id == "notif-123"
    assert result.message == "Order placed."
    assert result.order_id == ORDER_ID
    assert result.is_read is True


@patch("app.services.notification_service.get_user_role")
def test_list_notifications_for_user_returns_empty_for_unsupported_role(mock_get_user_role):
    """Unsupported roles should not receive any notifications."""
    mock_get_user_role.return_value = "guest"

    result = notification_service.list_notifications_for_user(USER_ID)

    assert not result


@patch("app.services.notification_service.get_order_record")
@patch("app.services.notification_service.list_notification_records")
@patch("app.services.notification_service.get_user_role")
def test_list_notifications_for_user_returns_only_visible_customer_notifications(
    mock_get_user_role,
    mock_list_notification_records,
    mock_get_order_record,
):
    """Customer listing should skip missing orders and orders owned by other users."""
    mock_get_user_role.return_value = "customer"
    mock_list_notification_records.return_value = [
        {
            "notification_id": "notif-visible",
            "message": "Newest",
            "timestamp": "2026-03-16T10:10:00+00:00",
            "order_id": "order-visible",
            "read_by_user_ids": [USER_ID],
        },
        {
            "notification_id": "notif-missing",
            "message": "Missing",
            "timestamp": "2026-03-16T10:05:00+00:00",
            "order_id": "order-missing",
            "read_by_user_ids": [],
        },
        {
            "notification_id": "notif-hidden",
            "message": "Hidden",
            "timestamp": "2026-03-16T10:00:00+00:00",
            "order_id": "order-hidden",
            "read_by_user_ids": [],
        },
    ]
    orders_by_id = {
        "order-visible": {
            "order_id": "order-visible",
            "customer_id": USER_ID,
            "restaurant_id": 1,
        },
        "order-hidden": {
            "order_id": "order-hidden",
            "customer_id": "other-user",
            "restaurant_id": 1,
        },
    }
    mock_get_order_record.side_effect = orders_by_id.get

    result = notification_service.list_notifications_for_user(USER_ID)

    assert [item.order_id for item in result] == ["order-visible"]
    assert [item.is_read for item in result] == [True]


@patch("app.services.notification_service.mark_notification_as_read")
@patch("app.services.notification_service.get_notification_record")
@patch("app.services.notification_service.get_user_role")
def test_mark_notification_as_read_for_user_raises_403_for_unsupported_role(
    mock_get_user_role,
    mock_get_notification_record,
    mock_mark_notification_as_read,
):
    """Unsupported roles should be rejected before any repo reads happen."""
    mock_get_user_role.return_value = "guest"

    with pytest.raises(HTTPException) as exc:
        notification_service.mark_notification_as_read_for_user("notif-123", USER_ID)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Access denied"
    mock_get_notification_record.assert_not_called()
    mock_mark_notification_as_read.assert_not_called()


@patch("app.services.notification_service.get_notification_record")
@patch("app.services.notification_service.get_user_role")
def test_mark_notification_as_read_for_user_raises_404_if_notification_not_found(
    mock_get_user_role,
    mock_get_notification_record,
):
    """Missing notifications should raise 404."""
    mock_get_user_role.return_value = "customer"
    mock_get_notification_record.return_value = None

    with pytest.raises(HTTPException) as exc:
        notification_service.mark_notification_as_read_for_user("notif-123", USER_ID)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Notification not found"


@patch("app.services.notification_service.get_order_record")
@patch("app.services.notification_service.get_notification_record")
@patch("app.services.notification_service.get_user_role")
def test_mark_notification_as_read_for_user_raises_404_if_order_not_found(
    mock_get_user_role,
    mock_get_notification_record,
    mock_get_order_record,
):
    """Notifications for deleted orders should raise 404."""
    mock_get_user_role.return_value = "customer"
    mock_get_notification_record.return_value = {
        "notification_id": "notif-123",
        "order_id": ORDER_ID,
    }
    mock_get_order_record.return_value = None

    with pytest.raises(HTTPException) as exc:
        notification_service.mark_notification_as_read_for_user("notif-123", USER_ID)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Notification not found"


@patch("app.services.notification_service.get_order_record")
@patch("app.services.notification_service.get_notification_record")
@patch("app.services.notification_service.get_user_role")
def test_mark_notification_as_read_for_user_raises_403_for_hidden_notification(
    mock_get_user_role,
    mock_get_notification_record,
    mock_get_order_record,
):
    """Users should not be able to mark invisible notifications as read."""
    mock_get_user_role.return_value = "customer"
    mock_get_notification_record.return_value = {
        "notification_id": "notif-123",
        "order_id": ORDER_ID,
    }
    mock_get_order_record.return_value = {
        "order_id": ORDER_ID,
        "customer_id": "other-user",
        "restaurant_id": 1,
    }

    with pytest.raises(HTTPException) as exc:
        notification_service.mark_notification_as_read_for_user("notif-123", USER_ID)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Not authorized to view this notification."


@patch("app.services.notification_service.mark_notification_as_read")
@patch("app.services.notification_service.get_order_record")
@patch("app.services.notification_service.get_notification_record")
@patch("app.services.notification_service.get_user_role")
def test_mark_notification_as_read_for_user_raises_500_if_update_fails(
    mock_get_user_role,
    mock_get_notification_record,
    mock_get_order_record,
    mock_mark_notification_as_read,
):
    """Repo update failures should raise 500."""
    mock_get_user_role.return_value = "customer"
    mock_get_notification_record.return_value = {
        "notification_id": "notif-123",
        "order_id": ORDER_ID,
    }
    mock_get_order_record.return_value = {
        "order_id": ORDER_ID,
        "customer_id": USER_ID,
        "restaurant_id": 1,
    }
    mock_mark_notification_as_read.return_value = None

    with pytest.raises(HTTPException) as exc:
        notification_service.mark_notification_as_read_for_user("notif-123", USER_ID)

    assert exc.value.status_code == 500
    assert exc.value.detail == "Failed to update notification"


@patch("app.services.notification_service.mark_notification_as_read")
@patch("app.services.notification_service.get_order_record")
@patch("app.services.notification_service.get_notification_record")
@patch("app.services.notification_service.get_user_role")
def test_mark_notification_as_read_for_user_returns_updated_response(
    mock_get_user_role,
    mock_get_notification_record,
    mock_get_order_record,
    mock_mark_notification_as_read,
):
    """Valid notification reads should return the updated notification response."""
    mock_get_user_role.return_value = "customer"
    mock_get_notification_record.return_value = {
        "notification_id": "notif-123",
        "message": "Order placed.",
        "timestamp": "2026-03-16T10:00:00+00:00",
        "order_id": ORDER_ID,
        "read_by_user_ids": [],
    }
    mock_get_order_record.return_value = {
        "order_id": ORDER_ID,
        "customer_id": USER_ID,
        "restaurant_id": 1,
    }
    mock_mark_notification_as_read.return_value = {
        "notification_id": "notif-123",
        "message": "Order placed.",
        "timestamp": "2026-03-16T10:00:00+00:00",
        "order_id": ORDER_ID,
        "read_by_user_ids": [USER_ID],
    }

    result = notification_service.mark_notification_as_read_for_user("notif-123", USER_ID)

    assert result.notification_id == "notif-123"
    assert result.order_id == ORDER_ID
    assert result.is_read is True
    mock_mark_notification_as_read.assert_called_once_with("notif-123", USER_ID)
