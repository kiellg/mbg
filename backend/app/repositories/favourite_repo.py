"""Repository functions for managing user favourites (restaurants and menu items)"""
from typing import Any
import shortuuid
from app.data.favourite_data import FAVOURITES

def _gen_favourite_id() -> str:
    """Generate a unique ID for a favourite record"""
    return shortuuid.ShortUUID().random(length=7)

def add_favourite(user_id: str, target_id: str, target_type: str) -> dict[str, Any]:
    """Add a restaurant or menu item to the user's favourites"""
    record = {
        "favourite_id": _gen_favourite_id(),
        "user_id": user_id,
        "target_id": target_id,
        "target_type": target_type,
    }
    FAVOURITES.append(record)
    return record

def remove_favourite(user_id: str, target_id: str, target_type: str) -> bool:
    """Remove a restaurant or menu item from the user's favourites"""
    for i, record in enumerate(FAVOURITES):
        if (record["user_id"] == user_id 
            and record["target_id"] == target_id
            and record["target_type"] == target_type):
            FAVOURITES.pop(i)
            return True
    return False

def get_favourites_for_user(user_id: str) -> list[dict[str, Any]]:
    """Get all favourite records for a given user"""
    return [r for r in FAVOURITES if r["user_id"] == user_id]

def is_favourite(user_id: str, target_id: str, target_type: str) -> bool:
    """Check if a restaurant or menu item is favourited by a user"""
    return any(
        r["user_id"] == user_id 
        and r["target_id"] == target_id
        and r["target_type"] == target_type
        for r in FAVOURITES
    )
