"""Schemas for order and order item payloads and responses."""

from decimal import Decimal
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import model_validator

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.schemas.coupon import CouponSnapshot


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
    SCHEDULED = "Scheduled"
    COOKING = "Cooking"
    OUT_FOR_DELIVERY = "Out for Delivery"
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
    menu_item_id: Optional[int] = None
    item_name: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    """Schema for creating a new order item."""

    order_id: Optional[str] = None


class OrderItemResponse(OrderItemBase):
    """Schema for returning an order item."""

    order_item_id: int
    order_id: str


class OrderBase(OrderSchemaModel):
    """Base schema for order fields."""
    customer_id: str
    restaurant_id: int
    delivery_address: str
    delivery_method: DeliveryMethod
    status: OrderStatus = OrderStatus.PENDING
    scheduled_time: Optional[datetime] = None
    is_scheduled: bool = False

    @model_validator(mode="after")
    def validate_schedule(self):
        """Ensure scheduled_time is set when is_scheduled is True"""
        if self.is_scheduled and self.scheduled_time is None:
            raise ValueError("" \
            "scheduled_time must be provided when is_scheduled is True")
        return self


class OrderCreate(OrderBase):
    """Schema for creating an order."""

    items: list[OrderItemCreate] = Field(default_factory=list)
    scheduled_time: Optional[datetime] = None
    coupon_code: Optional[str] = None
    coupon_snapshot: Optional[CouponSnapshot] = None


class OrderUpdate(OrderSchemaModel):
    """Schema for updating order fields."""

    status: Optional[OrderStatus] = None
    delivery_address: Optional[str] = None
    delivery_method: Optional[DeliveryMethod] = None
    items: Optional[list[OrderItemCreate]] = None


class PendingOrderItemUpdate(OrderSchemaModel):
    """Schema for replacing a pending order item from the public API."""

    menu_item_id: int
    quantity: int = Field(..., ge=1)


class PendingOrderUpdate(OrderSchemaModel):
    """Schema for updating a pending order through the public API."""

    delivery_address: Optional[str] = None
    delivery_method: Optional[DeliveryMethod] = None
    items: Optional[list[PendingOrderItemUpdate]] = None


class OrderResponse(OrderBase):
    """Schema for returning order details with cost breakdown."""

    order_id: str
    created_at: datetime
    driver_id: Optional[str] = None
    driver_name: Optional[str] = None
    items: list[OrderItemResponse] = Field(default_factory=list)
    coupon_code: Optional[str] = None
    subtotal: Decimal = Field(..., ge=0)
    discount: Decimal = Field(default=Decimal("0.00"), ge=0)
    discounted_subtotal: Decimal = Field(default=Decimal("0.00"), ge=0)
    tax: Decimal = Field(..., ge=0)
    delivery_fee: Decimal = Field(..., ge=0)
    total: Decimal = Field(..., ge=0)
