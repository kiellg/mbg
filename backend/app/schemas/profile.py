"""Schemas for profile update requests and responses"""

from typing import Optional

from pydantic import BaseModel
from app.schemas.order import DeliveryMethod

class CustomerProfileUpdateRequest(BaseModel):
    """Request schema for updating a customer profile"""
    name: Optional[str] = None
    delivery_address: Optional[str] = None

class CustomerProfileUpdateResponse(BaseModel):
    """Response schema returned after updating customer profile"""
    user_id: str
    name: str
    delivery_address: str
    message: str

class DriverProfileUpdateRequest(BaseModel):
    """Request schema for updating driver profile"""
    name: Optional[str] = None
    delivery_method: Optional[DeliveryMethod] = None
    is_available: Optional[bool] = None

class DriverProfileResponse(BaseModel):
    """Response schema returned for the logged in driver profile"""
    user_id: str
    name: str
    delivery_method: DeliveryMethod
    is_available: bool

class DriverProfileUpdateResponse(DriverProfileResponse):
    """Response schema returned after updating driver profile"""
    message: str

class RestaurantProfileUpdateRequest(BaseModel):
    """Request schema for updating restaurant details"""
    name: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[int] = None
    opening_hours: Optional[str] = None

class RestaurantProfileUpdateResponse(BaseModel):
    """Response schema returned after updating restaurant"""
    restaurant_id: int
    name: str
    address: str
    rating: Optional[int]
    opening_hours: str
    message: str
