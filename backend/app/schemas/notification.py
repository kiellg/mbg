"""Schemas for notification responses."""

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    """Response schema for notification records."""

    notification_id: str
    message: str
    timestamp: str
    order_id: str
    is_read: bool
