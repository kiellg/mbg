from typing import List
from pydantic import BaseModel, Field
from backend.app.schemas.menu import MenuItemOut

class RestaurantOut(BaseModel):
    id: int
    name: str
    address: str
    rating: int = Field(ge=1, le=5)
    opening_hours: str
    menu: List[MenuItemOut] = []
