"""Service layer for creating and managing order notifications."""

import logging
from datetime import datetime, timezone
from enum import Enum
from fastapi import HTTPException

from app.repositories.notification_repo import (
    create_notification,
    get_notification_record,
    list_notification_records,
    mark_notification_as_read,
)
from app.repositories.order_repo import get_order_record
from app.repositories.restaurant_repo import get_restaurant_record
from app.repositories.user_repo import get_user_role
from app.schemas.notification import NotificationResponse
from app.schemas.order import OrderStatus

ORDER_PLACED_MESSAGE = "Order placed."
ORDER_STATUS_CHANGED_MESSAGE_TEMPLATE = "Order status changed to {status}."
DRIVER_ASSIGNED_MESSAGE = "You have been assigned a delivery."
logger = logging.getLogger(__name__)
SUPPORTED_NOTIFICATION_ROLES = {"customer", "manager", "driver"}


class NotificationEventType(str, Enum):
    """Internal event types used for notification failure logging."""

    ORDER_PLACED = "order_placed"
    ORDER_STATUS_CHANGED = "order_status_changed"
    DRIVER_ASSIGNED = "driver_assigned"


def _log_notification_failure(
    event_type: NotificationEventType,
    order_id: str,
    error: Exception,
) -> None:
    """Log notification creation failures without breaking the main action."""
    logger.exception(
        "Notification creation failed. event_type=%s order_id=%s timestamp=%s error=%s",
        event_type.value,
        order_id,
        datetime.now(timezone.utc).isoformat(),
        str(error),
    )


def _create_notification_safely(
    message: str,
    order_id: str,
    event_type: NotificationEventType,
    audience_roles: list[str],
) -> dict:
    """Create a notification and suppress only notification creation failures."""
    try:
        return create_notification(
            message,
            order_id,
            event_type.value,
            audience_roles,
        )
    except Exception as error:  # pylint: disable=broad-exception-caught
        _log_notification_failure(event_type, order_id, error)
        return {}


def _notification_matches_audience(record: dict, role: str) -> bool:
    """Return whether the notification audience includes the current role."""
    return role in record.get("audience_roles", [])


def _notification_is_visible_to_user(order: dict, user_id: str, role: str) -> bool:
    """Return whether the user can view notifications for the given order."""
    if role == "customer":
        return order["customer_id"] == user_id

    if role == "manager":
        restaurant = get_restaurant_record(order["restaurant_id"])
        return restaurant is not None and restaurant.get("owner_id") == user_id

    if role == "driver":
        return order.get("driver_id") == user_id

    return False


def _get_order_status_changed_audience_roles(new_status: str) -> list[str]:
    """Return the least-privilege audience for an order status change."""
    if new_status == OrderStatus.COOKING:
        return ["customer", "manager"]

    if new_status == OrderStatus.CANCELLED:
        return ["customer", "manager"]

    if new_status in {OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DELIVERED}:
        return ["customer"]

    return ["customer"]


def _build_notification_response(record: dict, user_id: str) -> NotificationResponse:
    """Build a notification response for the requesting user."""
    return NotificationResponse(
        notification_id=record["notification_id"],
        message=record["message"],
        timestamp=record["timestamp"],
        order_id=record["order_id"],
        is_read=user_id in record.get("read_by_user_ids", []),
    )


def create_order_placed_notification(order_id: str) -> dict:
    """Create a notification for a newly placed order."""
    return _create_notification_safely(
        ORDER_PLACED_MESSAGE,
        order_id,
        NotificationEventType.ORDER_PLACED,
        ["customer"],
    )


def create_order_status_changed_notification(order_id: str, new_status: str) -> dict:
    """Create a notification for an order status change."""
    message = ORDER_STATUS_CHANGED_MESSAGE_TEMPLATE.format(status=new_status)
    return _create_notification_safely(
        message,
        order_id,
        NotificationEventType.ORDER_STATUS_CHANGED,
        _get_order_status_changed_audience_roles(new_status),
    )


def create_driver_assigned_notification(order_id: str) -> dict:
    """Create a notification for a newly assigned delivery driver."""
    return _create_notification_safely(
        DRIVER_ASSIGNED_MESSAGE,
        order_id,
        NotificationEventType.DRIVER_ASSIGNED,
        ["driver"],
    )


def list_notifications_for_user(user_id: str) -> list[NotificationResponse]:
    """Return newest-first notifications visible to the current user."""
    role = get_user_role(user_id)

    if role not in SUPPORTED_NOTIFICATION_ROLES:
        return []

    visible_notifications = []

    for record in list_notification_records():
        if not _notification_matches_audience(record, role):
            continue

        order = get_order_record(record["order_id"])
        if order is None:
            continue

        if not _notification_is_visible_to_user(order, user_id, role):
            continue

        visible_notifications.append(_build_notification_response(record, user_id))

    return visible_notifications


def mark_notification_as_read_for_user(
    notification_id: str,
    user_id: str,
) -> NotificationResponse:
    """Mark a visible notification as read for the current user."""
    role = get_user_role(user_id)
    if role not in SUPPORTED_NOTIFICATION_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")

    record = get_notification_record(notification_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    if not _notification_matches_audience(record, role):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this notification.",
        )

    order = get_order_record(record["order_id"])
    if order is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    if not _notification_is_visible_to_user(order, user_id, role):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this notification.",
        )

    updated_record = mark_notification_as_read(notification_id, user_id)
    if updated_record is None:
        raise HTTPException(status_code=500, detail="Failed to update notification")

    return _build_notification_response(updated_record, user_id)

