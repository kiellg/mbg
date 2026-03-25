"""Schemas for restaurant data"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.schemas.menu import MenuItemOut
from app.data.categories_data import VALID_CATEGORIES, VALID_DIETARY_TAGS

class RestaurantOut(BaseModel):
    """Schema for restaurant output with menu items and price statuses"""
    id: int
    name: str
    address: str
    rating: int = Field(ge=1, le=5)
    opening_hours: str
    cuisine_type: Optional[str] = None
    menu: List[MenuItemOut] = []

class RestaurantCreate(BaseModel):
    """Schema for creating a new restaurant"""
    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    rating: Optional[int] = Field(None, ge=1, le=5)
    opening_hours: str = ""
    cuisine_type: Optional[str] = None

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

    @field_validator("category_id")
    @classmethod
    def validate_category(cls, v):
        """Reject invalid category IDs"""
        if v not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category_id {v}. Valid options: {VALID_CATEGORIES}"
            )
        return v

    @field_validator("dietary_tag")
    @classmethod
    def validate_dietary_tag(cls, v):
        """Reject invalid dietary tags"""
        if v and v.lower() not in VALID_DIETARY_TAGS:
            raise ValueError(
                f"Invalid dietary_tag '{v}'. Valid options: {VALID_DIETARY_TAGS}"
            )
        return v.lower() if v else v

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

class RestaurantSearchResult(BaseModel):
    """Schema for restaurant search results"""
    id: int
    name: str
    address: str
    rating: int = Field(ge=1, le=5)

class MenuItemSearchResult(BaseModel):
    """Schema for menu item search results"""
    id: int
    name: str
    restaurant_id: int
    restaurant_name: str

class PaginatedRestaurants(BaseModel):
    """Schema for paginated restaurant results"""
    items: List[RestaurantOut]
    page: int
    limit: int
    total: int
