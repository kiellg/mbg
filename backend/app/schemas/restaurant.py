"""Schemas for restaurant data"""

from typing import List, Optional
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

class RestaurantCreate(BaseModel):
    """Schema for creating a new restaurant"""
    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    rating: Optional[int] = Field(None, ge=1, le=5)
    opening_hours: str = ""

class RestaurantUpdate(BaseModel):
    """Schema for updating restaurant details"""
    name: Optional[str] = Field(None, min_length=1)
    address: Optional[str] = Field(None, min_length=1)
    rating: Optional[int] = Field(None, ge=1, le=5)
    opening_hours: Optional[str] = None

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

class MenuItemUpdate(BaseModel):
    """Schema for updating a menu item"""
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    dietary_tag: Optional[str] = None
    price_cents: Optional[int] = Field(None, ge=0)
    is_visible: Optional[bool] = None
    is_active: Optional[bool] = None
    is_available: Optional[bool] = None
    category_id: Optional[int] = None
