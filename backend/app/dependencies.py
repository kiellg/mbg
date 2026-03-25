"""Shared FastAPI dependencies."""

from fastapi import HTTPException, Request
from app.repositories.session_repo import get_session


def get_current_user(request: Request) -> dict:
    """Dependency to get the current logged-in user based on session token."""
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Login required")
    session = get_session(session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Login required")
    return {"user_id": session["user_id"]}
