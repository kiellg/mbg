"""Schemas for notification responses."""

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    """Response schema for notification records."""

    message: str
    timestamp: str
    order_id: str
