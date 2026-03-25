"""Schemas for checkout request payload."""

from pydantic import BaseModel

from app.schemas.order import DeliveryMethod


class CheckoutRequest(BaseModel):
    """Payload for initiating a checkout."""

    delivery_method: DeliveryMethod
