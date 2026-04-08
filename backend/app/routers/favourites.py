"""API router for managing user favourites (restaurants and menu items)"""
from typing import Literal, Optional
from fastapi import APIRouter, Depends
from app.schemas.favourite import AddFavouriteRequest, FavouriteResponse, RemoveFavouriteResponse
from app.services import favourite_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/favourites", tags=["favourites"])

@router.post("", response_model=FavouriteResponse, status_code=201)
def add_favourite(
    body: AddFavouriteRequest,
    current_user: dict = Depends(get_current_user),
):
    """Add a restaurant or menu item to favourites"""
    return favourite_service.add_favourite_for_user(
        user_id=current_user["user_id"],
        target_id=body.target_id,
        target_type=body.target_type,
        restaurant_id=body.restaurant_id,
    )

@router.delete("", response_model=RemoveFavouriteResponse, status_code=200)
def remove_favourite(
    target_id: str,
    target_type: Literal["restaurant", "menu_item"],
    restaurant_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
):
    """Remove a restaurant or menu item from favourites"""
    return favourite_service.remove_favourite_for_user(
        user_id=current_user["user_id"],
        target_id=target_id,
        target_type=target_type,
        restaurant_id=restaurant_id,
    )

@router.get("", response_model=list[FavouriteResponse])
def list_favourites(
    current_user: dict = Depends(get_current_user),
):
    """List all favourites for the currently logged-in user"""
    return favourite_service.list_favourites_for_user(user_id=current_user["user_id"])
