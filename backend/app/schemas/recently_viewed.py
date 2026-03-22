"""Schemas for recently viewed items"""

from pydantic import BaseModel
from typing import List, Literal

class RecentlyViewedItem(BaseModel):
    """Represents a recently viewed item"""
    type: Literal["restaurant", "menu_item"]
    id: int

class RecentlyViewedResponse(BaseModel):
    """Response schema for recently viewed items"""
    item: List[RecentlyViewedItem]
