"""Service layer for creating order notifications."""

from backend.app.repositories.notification_repo import create_notification


def create_order_placed_notification(order_id: str) -> dict:
    """Create a notification for a newly placed order."""
    return create_notification("Order placed.", order_id)


def create_order_status_changed_notification(order_id: str, new_status: str) -> dict:
    """Create a notification for an order status change."""
    return create_notification(f"Order status changed to {new_status}.", order_id)
