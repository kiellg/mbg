"""Schemas for restaurant and menu filtering"""

from typing import Optional, List
from pydantic import BaseModel, Field

class RestaurantFilterRequest(BaseModel):
    """Request schema for filtering restaurants"""
    cuisine_types: Optional[List[str]] = None

    sort_by: Optional[str] = Field(
        default="rating",
        description="Sort restaurants by rating",
    )

    order: Optional[str] = Field(
        default="desc",
        description="Sorting order: asc or desc",
    )

class MenuItemFilterRequest(BaseModel):
    """Request schema for filtering menu items"""
    categories: Optional[List[int]] = None
    dietary_tags: Optional[List[str]] = None
    min_price_cents: Optional[int] = None
    max_price_cents: Optional[int] = None

    sort_by: Optional[str] = Field(
        default="price",
        description="Sort menu items by price",
    )

    order: Optional[str] = Field(
        default="asc",
        description="Sorting order: asc or desc",
    )
