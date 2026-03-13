"""Service layer containing business logic for user registration and login"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import HTTPException

from backend.app.repositories.user_repo import(
    get_user_by_email,
    get_user_by_id,
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
    store_password_reset_token,
    get_password_reset_token,
    delete_password_reset_token,
)

from backend.app.repositories.session_repo import(
    get_session,
    delete_session,
)

from backend.app.repositories.login_attempt_repo import(
    create_login_attempt,
)

MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCK_DURATION = timedelta(hours=1)
RESET_TOKEN_DURATION = timedelta(hours=1)

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
        create_login_attempt("", email, False, "invalid_credentials")

        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    lock_until = get_lock_until(email)

    if lock_until and datetime.now() < lock_until:
        create_login_attempt(user["user_id"], email, False, "account_locked")

        raise HTTPException(
            status_code=401,
            detail="Account is locked. Please try again later.",
        )

    password_hash = hash_password(password)

    if user["password_hash"] != password_hash:
        increment_failed_login_attempts(email)

        failed_attempts = get_failed_login_attempts(email)

        create_login_attempt(user["user_id"], email, False, "invalid_credentials")

        if failed_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
            set_lock_until(email, datetime.now() + LOCK_DURATION)

            create_login_attempt(user["user_id"], email, False, "account_locked")

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

    create_login_attempt(user["user_id"], email, True, None)

    role = get_user_role(user["user_id"])

    return{
        "message": "Login successful!",
        "user_id": user["user_id"],
        "email": user["email"],
        "role": role,
    }

def request_password_reset(email: str):
    """Generate a password reset token for a user"""
    user = get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = secrets.token_urlsafe(32)

    expires_at = datetime.now() + RESET_TOKEN_DURATION

    store_password_reset_token(
        token,
        user["user_id"],
        expires_at,
    )

    return token

def reset_password(token: str, new_password: str):
    """Reset a user's password using a reset token"""
    record = get_password_reset_token(token)

    if not record:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    if datetime.now() > record["expires_at"]:
        delete_password_reset_token(token)
        raise HTTPException(status_code=400, detail="Reset token expired")

    user = get_user_by_id(record["user_id"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["password_hash"] = hash_password(new_password)

    delete_password_reset_token(token)

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
