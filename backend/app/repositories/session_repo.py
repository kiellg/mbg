"""Repository layer for session storage"""

import secrets
from typing import Dict, Any, Optional

from backend.app.data import session_store

def create_session(user_id: int) -> str:
    """Create a new session for a user"""
    session_token = secrets.token_hex(16)

    session_store.SESSIONS[session_token] = {
        "user_id": user_id,
    }
    return session_token

def get_session(session_token: str) -> Optional[Dict[str, Any]]:
    """Return a session by token"""
    return session_store.SESSIONS.get(session_token)

def delete_session(session_token: str) -> bool:
    """Delete a session by token"""
    if session_token not in session_store.SESSIONS:
        return False

    del session_store.SESSIONS[session_token]
    return True

def reset_session():
    """Reset all sessions"""
    session_store.SESSIONS = {}
