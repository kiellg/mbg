"""Schemas for checkout request payload."""

from datetime import datetime

from typing import Optional

from pydantic import BaseModel

from app.schemas.order import DeliveryMethod


class CheckoutRequest(BaseModel):
    """Payload for initiating a checkout."""

    delivery_method: DeliveryMethod
    coupon_code: Optional[str] = None
    scheduled_time: Optional[datetime] = None
