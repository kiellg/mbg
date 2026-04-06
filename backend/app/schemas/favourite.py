"""Schemas for user favourites (restaurants and menu items)"""
from typing import Literal, Optional
from pydantic import BaseModel, model_validator

class AddFavouriteRequest(BaseModel):
    """Request schema for adding a favourite restaurant or menu item"""
    target_id: str
    target_type: Literal["restaurant", "menu_item"]
    restaurant_id: Optional[int] = None
    @model_validator(mode="after")
    def restaurant_id_required_for_menu_item(self) -> "AddFavouriteRequest":
        """Ensure that restaurant_id is provided when target_type is 'menu_item'"""
        if self.target_type == "menu_item" and self.restaurant_id is None:
            raise ValueError("restaurant_id is required when target_type is 'menu_item'")
        return self

class FavouriteResponse(BaseModel):
    """Response schema for a favourite restaurant or menu item"""
    favourite_id: str
    user_id: str
    target_id: str
    target_type: str
