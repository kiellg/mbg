"""Schemas for search suggestions"""

from typing import List, Optional
from pydantic import BaseModel

class suggestion_item(BaseModel):
    """Represents a single search suggestion"""
    type: str
    id: str
    name: str
    restaurant_id: Optional[int] = None

class suggestion_response(BaseModel):
    """Response schema for search suggestions"""
    suggestions: List[suggestion_item]
