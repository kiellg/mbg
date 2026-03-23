"""Schemas for recently viewed items"""

from typing import List, Literal
from pydantic import BaseModel

class RecentlyViewedItem(BaseModel):
    """Represents a recently viewed item"""
    type: Literal["restaurant", "menu_item"]
    id: int

class RecentlyViewedResponse(BaseModel):
    """Response schema for recently viewed items"""
    items: List[RecentlyViewedItem]
