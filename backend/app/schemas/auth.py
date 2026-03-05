"""Schemas for authentication requests and responses"""

from pydantic import BaseModel, EmailStr
from typing import Literal

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["customer", "manager", "driver"]

class RegisterResponse(BaseModel):
    user_id: int
    email: EmailStr
