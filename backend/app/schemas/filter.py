"""Schemas for restaurant and menu filtering"""

from typing import Optional, List
from pydantic import BaseModel

class RestaurantFilterRequest(BaseModel):
    """Request schema for filtering restaurants"""
    cuisine_types: Optional[List[str]] = None

class MenuItemFilterRequest(BaseModel):
    """Request schema for filtering menu items"""
    categories: Optional[List[int]] = None
    dietary_tags: Optional[List[str]] = None
    min_price_cents: Optional[int] = None
    max_price_cents: Optional[int] = None
