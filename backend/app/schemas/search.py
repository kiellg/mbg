"""Schemas for search suggestions"""

from typing import List, Optional
from pydantic import BaseModel

class SuggestionItem(BaseModel):
    """Represents a single search suggestion"""
    type: str
    id: str
    name: str
    restaurant_id: Optional[int] = None

class SuggestionResponse(BaseModel):
    """Response schema for search suggestions"""
    suggestions: List[SuggestionItem]
