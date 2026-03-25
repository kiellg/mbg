"""Repository for login attempt records"""

from datetime import datetime
from typing import Dict, List

from app.data.login_attempts_data import LOGIN_ATTEMPTS

def create_login_attempt(
        user_id: str,
        email: str,
        success: bool,
        reason: str | None = None,
) -> None:
    """Create a login attempt record"""
    LOGIN_ATTEMPTS.append(
        {
            "user_id": user_id,
            "email": email,
            "success": success,
            "reason": reason,
            "timestamp": datetime.utcnow(),
        }
    )

def get_login_attempts_by_user(user_id: str) -> List[Dict]:
    """Return login attempts for a specific user"""
    return[
        attempt for attempt in LOGIN_ATTEMPTS
        if attempt["user_id"] == user_id
    ]

def reset_login_attempts() -> None:
    """Clear stored login attempts"""
    LOGIN_ATTEMPTS.clear()
