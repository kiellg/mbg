"""Tests for logout service logic"""

import pytest
from fastapi import HTTPException

from backend.app.repositories.session_repo import create_session, reset_session
from backend.app.services.auth_service import(
    logout_user,
    get_current_user_session,
)

def setup_function():
    """Reset session data before each test"""
    reset_session()

def test_logout_user_removes_valid_session():
    """Logout should remove an existing session"""
    session_token = create_session(1)

    response = logout_user(session_token)

    assert response == {
        "message": "Logout successful",
    }

def test_logout_user_raises_for_invalid_session():
    """Logout should fail for an invalid session"""
    with pytest.raises(HTTPException) as error:
        logout_user("invalid_token")

    assert error.value.status_code == 401
    assert error.value.detail == "Invalid session"

def test_get_current_user_session_returns_session():
    """Current user session should be returned for a valid token"""
    session_token = create_session(1)

    session = get_current_user_session(session_token)

    assert session == {
        "user_id": 1,
    }

def test_get_current_user_session_requires_login():
    """Current user session should fail for an invalid token"""
    with pytest.raises(HTTPException) as error:
        get_current_user_session("invalid_token")

    assert error.value.status_code == 401
    assert error.value.detail == "Login required"
