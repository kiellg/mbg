"""Schemas for authentication requests and responses"""

from typing import Literal, Optional

from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    """Request schema for user registration"""
    name: str
    email: EmailStr
    password: str
    role: Literal["customer", "manager", "driver"]

class RegisterResponse(BaseModel):
    """Response schema returned after registration"""
    user_id: str
    email: EmailStr

class LoginRequest(BaseModel):
    """Request schema for user login"""
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    """Response schema returned after succcessful login"""
    message: str
    user_id: str
    email: EmailStr
    role: Optional[str]

class PasswordResetRequest(BaseModel):
    """Request schema for sending a password reset link"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Request schema for confirming a password reset"""
    token: str
    new_password: str
