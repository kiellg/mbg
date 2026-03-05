"""API routes related to authentication"""

from fastapi import APIRouter

from app.schemas.auth import RegisterRequest, RegisterResponse
from app.services.auth_service import register_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest):
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
