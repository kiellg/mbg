"""Pydantic schemas for cart request validation and API responses."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    """Schema for adding a new item to the cart."""
    menu_item_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")

class CartItemUpdate(BaseModel):
    """Schema for updating the quantity of an existing cart item."""
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")

class CartItemResponse(BaseModel):
    """Schema for returning a single cart item."""
    id: int
    cart_id: int
    menu_item_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")
    item_name: str
    unit_price_cents: int
    item_subtotal_cents: int
    display_unit_price: str = Field(..., description="Formatted price for display")
    display_item_subtotal: str = Field(..., description="Formatted subtotal for display")

class CartResponse(BaseModel):
    """Schema for returning the full cart."""
    id: int
    customer_id: int
    restaurant_id: int
    created_at: datetime
    items: List[CartItemResponse] = []
    cart_subtotal_cents: int
    display_cart_subtotal: str = Field(..., description="Formatted cart subtotal for display")
