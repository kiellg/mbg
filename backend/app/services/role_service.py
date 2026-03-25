"""Service layer for role based access checks"""

from typing import Any, Dict, Optional
from fastapi import HTTPException

from app.services.auth_service import get_current_user_session
from app.repositories.user_repo import get_user_role

def require_role(session_token: Optional[str], allowed_roles: list[str]) -> Dict[str, Any]:
    """Ensure the authenticated user has an allowed role"""
    if not session_token:
        raise HTTPException(status_code=401, detail="Login required")

    session = get_current_user_session(session_token)

    user_id = session["user_id"]
    role = get_user_role(user_id)

    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Access denied")

    return session

def require_customer(session_token: str) -> Dict[str, Any]:
    """Ensure the authenticated user is a customer"""
    return require_role(session_token, ["customer"])

def require_manager(session_token: str) -> Dict[str, Any]:
    """Ensure the authenticated user is a manager"""
    return require_role(session_token, ["manager"])

def require_driver(session_token: str) -> Dict[str, Any]:
    """Ensure the authenticated user is a driver"""
    return require_role(session_token, ["driver"])
