"""Service layer for creating and reading order notifications."""

import logging
from datetime import datetime, timezone
from enum import Enum

from backend.app.repositories.notification_repo import (
    create_notification,
    list_notification_records,
)
from backend.app.repositories.order_repo import get_order_record
from backend.app.repositories.restaurant_repo import get_restaurant_record
from backend.app.repositories.user_repo import get_user_role
from backend.app.schemas.notification import NotificationResponse

ORDER_PLACED_MESSAGE = "Order placed."
ORDER_STATUS_CHANGED_MESSAGE_TEMPLATE = "Order status changed to {status}."
DRIVER_ASSIGNED_MESSAGE = "You have been assigned a delivery."
logger = logging.getLogger(__name__)


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
) -> dict:
    """Create a notification and suppress only notification creation failures."""
    try:
        return create_notification(message, order_id)
    except Exception as error:  # pylint: disable=broad-exception-caught
        _log_notification_failure(event_type, order_id, error)
        return {}


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


def create_order_placed_notification(order_id: str) -> dict:
    """Create a notification for a newly placed order."""
    return _create_notification_safely(
        ORDER_PLACED_MESSAGE,
        order_id,
        NotificationEventType.ORDER_PLACED,
    )


def create_order_status_changed_notification(order_id: str, new_status: str) -> dict:
    """Create a notification for an order status change."""
    message = ORDER_STATUS_CHANGED_MESSAGE_TEMPLATE.format(status=new_status)
    return _create_notification_safely(
        message,
        order_id,
        NotificationEventType.ORDER_STATUS_CHANGED,
    )


def create_driver_assigned_notification(order_id: str) -> dict:
    """Create a notification for a newly assigned delivery driver."""
    return _create_notification_safely(
        DRIVER_ASSIGNED_MESSAGE,
        order_id,
        NotificationEventType.DRIVER_ASSIGNED,
    )


def list_notifications_for_user(user_id: str) -> list[NotificationResponse]:
    """Return newest-first notifications visible to the current user."""
    role = get_user_role(user_id)

    if role not in {"customer", "manager", "driver"}:
        return []

    visible_notifications = []

    for record in list_notification_records():
        order = get_order_record(record["order_id"])
        if order is None:
            continue

        if not _notification_is_visible_to_user(order, user_id, role):
            continue

        visible_notifications.append(NotificationResponse(**record))

    return visible_notifications
