"""Service layer for admin user profile management"""
from fastapi import HTTPException

from app.repositories import user_repo
from app.schemas.user import ProfileResponse
from app.repositories import order_repo, restaurant_repo, session_repo

def list_all_profiles() -> list[dict]:
    """Return all user profiles with resolved roles"""
    raw_profiles = user_repo.list_all_profiles()
    return [
        ProfileResponse.model_validate(p).model_dump()
        for p in raw_profiles
    ]

def delete_user(user_id: str) -> None:
    """Delete a user by ID, revoking sessions and cleaning up cross-entity references"""
    if user_repo.is_admin(user_id):
        raise HTTPException(
            status_code=403,
            detail="Admin accounts cannot be deleted.",
        )
    deleted = user_repo.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found.")

    session_repo.delete_sessions_for_user(user_id)
    restaurant_repo.clear_owner_reference(user_id)
    order_repo.clear_driver_reference(user_id)
    