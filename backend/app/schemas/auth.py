"""Schemas for authentication requests and responses"""

from typing import Literal

from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    """Request schema for user registration"""
    name: str
    email: EmailStr
    password: str
    role: Literal["customer", "manager", "driver"]

class RegisterResponse(BaseModel):
    """Response schema returned after registration"""
    user_id: int
    email: EmailStr
