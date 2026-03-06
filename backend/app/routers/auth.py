"""API routes related to authentication"""

from fastapi import APIRouter, Response

from backend.app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
)
from backend.app.services.auth_service import register_user, authenticate_user
from backend.app.data.session_store import create_session

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
