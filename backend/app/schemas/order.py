"""Schemas for order and order item payloads and responses."""

from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class OrderSchemaModel(BaseModel):
    """Shared schema settings for order models."""

    model_config = ConfigDict(
        validate_assignment=True,
    )

    @field_serializer("*", when_used="json", check_fields=False)
    def _serialize_decimal_for_json(self, value):
        """Serialize Decimal values as strings for JSON responses."""
        if isinstance(value, Decimal):
            return str(value)
        return value


class OrderStatus(str, Enum):
    """Valid statuses for an order."""

    PENDING = "Pending"
    COOKING = "Cooking"
    OUT_FOR_DELIVERY = "OutForDelivery"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class DeliveryMethod(str, Enum):
    """Valid delivery methods for an order."""

    WALK = "walk"
    BIKE = "bike"
    CAR = "car"


class OrderItemBase(OrderSchemaModel):
    """Base schema for order item fields."""

    quantity: int = Field(..., ge=1)
    item_price: Decimal = Field(..., ge=0)


class OrderItemCreate(OrderItemBase):
    """Schema for creating a new order item."""

    order_id: Optional[str] = None


class OrderItemResponse(OrderItemBase):
    """Schema for returning an order item."""

    order_item_id: int
    order_id: str


class OrderBase(OrderSchemaModel):
    """Base schema for order fields."""

    delivery_address: str
    delivery_method: DeliveryMethod
    status: OrderStatus = OrderStatus.PENDING # Current order status is clearly displayed (US48)


class OrderCreate(OrderBase):
    """Schema for creating an order."""

    items: list[OrderItemCreate] = Field(default_factory=list)


class OrderUpdate(OrderSchemaModel):
    """Schema for updating order fields."""

    status: Optional[OrderStatus] = None
    delivery_address: Optional[str] = None
    delivery_method: Optional[DeliveryMethod] = None
    items: Optional[list[OrderItemCreate]] = None


class OrderResponse(OrderBase):
    """Schema for returning order details with cost breakdown."""

    order_id: str
    items: list[OrderItemResponse] = Field(default_factory=list)
    subtotal: Decimal = Field(..., ge=0)
    tax: Decimal = Field(..., ge=0)
    delivery_fee: Decimal = Field(..., ge=0)
    total: Decimal = Field(..., ge=0)
