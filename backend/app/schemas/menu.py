"""Schemas for menu items and categories"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel

class PriceStatus(str, Enum):
    """Enum for price status of menu items"""
    ok = "ok"
    missing = "missing"
    invalid = "invalid"

class MenuCategory(BaseModel):
    """Schema for menu item categories"""
    id: int
    name: str

class MenuItemOut(BaseModel):
    """Schema for menu items with price status and display price"""
    id: int
    name: str

    price_cents: Optional[int] = None
    display_price: Optional[str] = None
    price_status: PriceStatus = PriceStatus.ok

    description: str = ""
    dietary_tag: str = ""

    is_visible: bool = True
    is_active: bool = True
    is_available: bool = True

    category: Optional[MenuCategory] = None


