"""Service layer for managing user favourites (restaurants and menu items)"""
from fastapi import HTTPException
from app.repositories.favourite_repo import (
    add_favourite,
    remove_favourite,
    get_favourites_for_user,
    is_favourite,
)
from app.repositories.restaurant_repo import get_restaurant_record, get_menu_item
from app.repositories.user_repo import get_user_by_id
from app.schemas.favourite import FavouriteResponse

def _validate_target_exists(
    target_id: str,
    target_type: str,
    restaurant_id: int | None = None,
) -> None:
    """Validate that the target restaurant or menu item exists"""
    try:
        numeric_id = int(target_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target_id '{target_id}': must be a numeric value.",
        ) from exc

    if target_type == "restaurant":
        if get_restaurant_record(numeric_id) is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")

    elif target_type == "menu_item":
        if get_menu_item(restaurant_id, numeric_id) is None:
            raise HTTPException(status_code=404, detail="Menu item not found")

def add_favourite_for_user(
    user_id: str,
    target_id: str,
    target_type: str,
    restaurant_id: int | None = None,
) -> FavouriteResponse:
    """Add a restaurant or menu item to the user's favourites"""
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    _validate_target_exists(target_id, target_type, restaurant_id)

    if is_favourite(user_id, target_id, target_type, restaurant_id):
        raise HTTPException(status_code=409, detail="Already in favourites")

    record = add_favourite(user_id, target_id, target_type, restaurant_id)
    return FavouriteResponse(**record)

def remove_favourite_for_user(
    user_id: str,
    target_id: str,
    target_type: str,
    restaurant_id: int | None = None,
) -> dict:
    """Remove a restaurant or menu item from the user's favourites"""
    if not is_favourite(user_id, target_id, target_type, restaurant_id):
        raise HTTPException(status_code=404, detail="Favourite not found")

    remove_favourite(user_id, target_id, target_type, restaurant_id)
    return {"detail": "Favourite removed successfully"}

def list_favourites_for_user(user_id: str) -> list[FavouriteResponse]:
    """List all favourites for a given user"""
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    records = get_favourites_for_user(user_id)
    return [FavouriteResponse(**r) for r in records]
