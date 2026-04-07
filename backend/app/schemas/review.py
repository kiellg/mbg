"""This module defines the Pydantic schemas for review-related operations."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class ReviewCreate(BaseModel):
    """Schema for creating a new review"""
    order_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    """Schema for returning review details"""
    review_id: str
    customer_id: str
    order_id: str
    restaurant_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
