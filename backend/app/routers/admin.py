#pylint: disable=unused-argument, duplicate-code
"""Router for admin user profile management endpoints"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, Request, status

from app.schemas.user import ProfileResponse
from app.services import admin_service
from app.services.role_service import require_admin

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

def get_session_token(
    request: Request,
    session_token: Optional[str] = Header(default=None),
) -> Optional[str]:
    """Return session token from header or cookie"""
    if session_token:
        return session_token
    return request.cookies.get("session_token")

def authenticate_admin(
    request: Request,
    session_token: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """Authenticate the user and ensure they are an admin"""
    return require_admin(get_session_token(request, session_token))

@router.get("", response_model=list[ProfileResponse])
def list_profiles(
    request: Request,
    session_token: Optional[str] = Header(default=None),
):
    """List all user profiles with their resolved roles"""
    authenticate_admin(request, session_token)
    return admin_service.list_all_profiles()

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    request: Request,
    session_token: Optional[str] = Header(default=None),
):
    """Delete a user and their role profile from all stores but not admin"""
    authenticate_admin(request, session_token)
    admin_service.delete_user(user_id)
