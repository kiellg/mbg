"""Schemas for user profile responses"""
from typing import Optional
from pydantic import BaseModel

class ProfileResponse(BaseModel):
    """Schema for user profile response"""
    user_id: str
    name: str
    email: str
    role: Optional[str] = None
