"""API routes related to authentication"""

from fastapi import APIRouter, Response, Request, HTTPException, Depends

from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    logout_user,
    request_password_reset,
    reset_password,
)

from app.repositories.session_repo import create_session

from app.dependencies import get_current_user

from app.data import users_data
from app.data import session_store

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest):
    """Register a new user account"""
    user = register_user(
        payload.name,
        payload.email,
        payload.password,
        payload.role,
    )

    return{
        "user_id": user["user_id"],
        "email": user["email"],
    }

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response):
    """Log in a registered user"""
    user = authenticate_user(
        payload.email,
        payload.password,
    )

    session_token = create_session(user["user_id"])

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
    )

    return{
        "message": user["message"],
        "user_id": user["user_id"],
        "email": user["email"],
        "role": user["role"],
    }

@router.post("/logout")
def logout(request: Request, response: Response):
    """Log out the current user"""
    session_token = request.cookies.get("session_token")

    if not session_token:
        raise HTTPException(status_code=401, detail="Login required")

    result = logout_user(session_token)

    response.delete_cookie(key="session_token")

    return result

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Return the currently authenticated user"""
    return {"user_id": current_user["user_id"]}

@router.post("/forgot-password")
def forgot_password(payload: PasswordResetRequest):
    """Send a password reset token"""
    token = request_password_reset(payload.email)

    return {"reset_token": token}

@router.post("/reset-password")
def confirm_password_reset(payload: PasswordResetConfirm):
    """Reset a password using a reset token"""
    reset_password(
        payload.token,
        payload.new_password,
    )

    return {"message": "Password reset successful"}

@router.get("/debug/users")
def debug_users():
    """Debug to get lists of registered users."""
    return users_data.USERS

@router.get("/debug/sessions")
def debug_sessions():
    """Debug to get lists of current sessions"""
    return session_store.SESSIONS
