"""Simulated session storage for authenticated users"""

import secrets
from typing import Dict, Any, Optional

_SESSIONS: Dict[str, Dict[str, Any]] = {}

def create_session(user_id: int) -> str:
    """Create a new session for a user"""
    session_token = secrets.token_hex(16)

    _SESSIONS[session_token] = {
        "user_id": user_id,
    }
    return session_token

def get_session(session_token: str) -> Optional[Dict[str, Any]]:
    """Return a session by token"""
    return _SESSIONS.get(session_token)

def reset_session():
    """Reset all sessions"""
    global _SESSIONS  # pylint: disable=global-statement
    _SESSIONS = {}
