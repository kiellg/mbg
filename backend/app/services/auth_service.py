"""Service layer containing business logic for user registration and login"""

import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import HTTPException

from backend.app.repositories.user_repo import(
    get_user_by_email,
    create_user,
    create_customer,
    create_manager,
    create_driver,
    get_user_role,
    increment_failed_login_attempts,
    reset_failed_login_attempts,
    get_failed_login_attempts,
    set_lock_until,
    get_lock_until,
)

from backend.app.repositories.session_repo import(
    get_session,
    delete_session,
)

MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCK_DURATION = timedelta(hours=1)

def hash_password(password: str) -> str:
    """Hash the password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name: str, email: str, password: str, role: str):
    """Register a user if the email doesn't already exist"""
    if get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email already exists")

    password_hash = hash_password(password)

    user = create_user(name, email, password_hash)

    if role == "customer":
        create_customer(user["user_id"])

    elif role == "manager":
        create_manager(user["user_id"])

    elif role == "driver":
        create_driver(user["user_id"])

    return user

def authenticate_user(email: str, password: str):
    """Authenticate a user with email and password"""
    user = get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    lock_until = get_lock_until(email)

    if lock_until and datetime.now() < lock_until:
        raise HTTPException(
            status_code=401,
            detail="Account is locked. Please try again later.",
        )

    password_hash = hash_password(password)

    if user["password_hash"] != password_hash:
        increment_failed_login_attempts(email)

        failed_attempts = get_failed_login_attempts(email)

        if failed_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
            set_lock_until(email, datetime.now() + LOCK_DURATION)
            raise HTTPException(
                status_code=401,
                detail="Account is locked. Please try again later.",
            )

        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    reset_failed_login_attempts(email)
    set_lock_until(email, None)

    role = get_user_role(user["user_id"])

    return{
        "message": "Login successful!",
        "user_id": user["user_id"],
        "email": user["email"],
        "role": role,
    }

def logout_user(session_token: str):
    """Log out a user by deleting the session"""
    deleted = delete_session(session_token)

    if not deleted:
        raise HTTPException(status_code=401, detail="Invalid session")

    return{
        "message": "Logout successful",
    }

def get_current_user_session(session_token: str) -> Dict[str, Any]:
    """Return the current user session"""
    session = get_session(session_token)

    if not session:
        raise HTTPException(status_code=401, detail="Login required")

    return session
