"""Schemas for restaurant data"""

from typing import List
from pydantic import BaseModel, Field
from backend.app.schemas.menu import MenuItemOut

class RestaurantOut(BaseModel):
    """Schema for restaurant output with menu items and price statuses"""
    id: int
    name: str
    address: str
    rating: int = Field(ge=1, le=5)
    opening_hours: str
    menu: List[MenuItemOut] = []

class MenuItemCreate(BaseModel):
    """Schema for creating a new menu item"""
    name: str = Field(..., min_length=1)
    description: str = ""
    dietary_tag: str = ""
    price_cents: int = Field(..., ge=0, description="Price in cents, must be non-negative")
    is_visible: bool = True
    is_active: bool = True
    is_available: bool = True
    category_id: int
