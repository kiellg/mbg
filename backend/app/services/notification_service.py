"""Service layer for creating order notifications."""

from backend.app.repositories.notification_repo import create_notification

ORDER_PLACED_MESSAGE = "Order placed."
ORDER_STATUS_CHANGED_MESSAGE_TEMPLATE = "Order status changed to {status}."


def create_order_placed_notification(order_id: str) -> dict:
    """Create a notification for a newly placed order."""
    return create_notification(ORDER_PLACED_MESSAGE, order_id)


def create_order_status_changed_notification(order_id: str, new_status: str) -> dict:
    """Create a notification for an order status change."""
    message = ORDER_STATUS_CHANGED_MESSAGE_TEMPLATE.format(status=new_status)
    return create_notification(message, order_id)
