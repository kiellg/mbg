"""Schemas for profile update requests and responses"""

from typing import Optional

from pydantic import BaseModel

class CustomerProfileUpdateRequest(BaseModel):
    """Request schema for updating a customer profile"""
    name: Optional[str] = None
    delivery_address: Optional[str] = None

class CustomerProfileUpdateResponse(BaseModel):
    """Response schema returned after updating customer profile"""
    user_id: int
    name: str
    delivery_address: str
    message: str

class DriverProfileUpdateRequest(BaseModel):
    """Request schema for updating driver profile"""
    name: Optional[str] = None

class DriverProfileUpdateResponse(BaseModel):
    """Response schema returned after updating driver profile"""
    user_id: int
    name: str
    message: str

class RestaurantProfileUpdateRequest(BaseModel):
    """Request schema for updating restaurant details"""
    name: Optional[str] = None
    address: Optional[str] = None

class RestaurantProfileUpdateResponse(BaseModel):
    """Response schema returned after updating restaurant"""
    restaurant_id: int
    name: str
    address: str
    message: str
