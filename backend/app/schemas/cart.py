"""Pydantic schemas for cart request validation and API responses."""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CartItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")

class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    menu_item_id: int
    quantity: int
    item_name: str
    unit_price_cents: int
    subtotal_cents: int

class CartResponse(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    created_at: datetime
    items: List[CartItemResponse] = []
    total_cents: int
    