"""Schemas for checkout request payload."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, model_validator

from app.schemas.order import DeliveryMethod


class CheckoutRequest(BaseModel):
    """Payload for initiating a checkout."""

    delivery_method: DeliveryMethod
    coupon_code: Optional[str] = None
    is_scheduled: bool = False
    scheduled_time: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_schedule(self):
        if self.is_scheduled and self.scheduled_time is None:
            raise ValueError("scheduled_time is required when is_scheduled is True")
        return self
