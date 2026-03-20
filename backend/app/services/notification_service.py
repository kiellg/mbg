"""Service layer for creating and reading order notifications."""

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


def create_order_placed_notification(order_id: str) -> dict:
    """Create a notification for a newly placed order."""
    return create_notification(ORDER_PLACED_MESSAGE, order_id)


def create_order_status_changed_notification(order_id: str, new_status: str) -> dict:
    """Create a notification for an order status change."""
    message = ORDER_STATUS_CHANGED_MESSAGE_TEMPLATE.format(status=new_status)
    return create_notification(message, order_id)


def list_notifications_for_user(user_id: str) -> list[NotificationResponse]:
    """Return newest-first notifications visible to the current user."""
    role = get_user_role(user_id)

    if role not in {"customer", "manager"}:
        return []

    visible_notifications = []

    for record in list_notification_records():
        order = get_order_record(record["order_id"])
        if order is None:
            continue

        if role == "customer":
            if order["customer_id"] != user_id:
                continue
        else:
            restaurant = get_restaurant_record(order["restaurant_id"])
            if restaurant is None or restaurant.get("owner_id") != user_id:
                continue

        visible_notifications.append(NotificationResponse(**record))

    return visible_notifications
