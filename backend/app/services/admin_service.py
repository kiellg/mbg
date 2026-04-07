"""Service layer for admin user profile management"""
from fastapi import HTTPException

from app.repositories import user_repo
from app.schemas.user import ProfileResponse

def list_all_profiles() -> list[dict]:
    """Return all user profiles with resolved roles"""
    raw_profiles = user_repo.list_all_profiles()
    return [
        ProfileResponse.model_validate(p).model_dump()
        for p in raw_profiles
    ]

def delete_user(user_id: str) -> None:
    """Delete a user by ID. Raises 403 if admin, 404 if not found"""
    if user_repo.is_admin(user_id):
        raise HTTPException(
            status_code=403,
            detail="Admin accounts cannot be deleted.",
        )
    deleted = user_repo.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found.")
    