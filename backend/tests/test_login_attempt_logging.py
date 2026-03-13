"""Tests for login attempt logging"""

from fastapi.testclient import TestClient

from backend.main import app
from backend.app.data.login_attempts_data import LOGIN_ATTEMPTS
from backend.app.repositories.user_repo import create_user, reset_users
from backend.app.services.auth_service import hash_password

client = TestClient(app)

def setup_function():
    """Reset db before each test"""
    reset_users()
    LOGIN_ATTEMPTS.clear()

def test_failed_login_attempt_is_logged():
    """Failed login attempts should be recorded"""
    create_user("test", "test@email.com", hash_password("correct_pw"))

    response = client.post(
        "/auth/login",
        json={
            "email": "test@email.com",
            "password": "wrong_pw",
        },
    )

    assert response.status_code == 401
    assert len(LOGIN_ATTEMPTS) == 1
    assert LOGIN_ATTEMPTS[0]["success"] is False

def test_successful_login_attempt_is_logged():
    """Successful login attempts should be recorded"""
    create_user("test", "test@email.com", hash_password("correct_pw"))

    response = client.post(
        "/auth/login",
        json={
            "email": "test@email.com",
            "password": "correct_pw",
        },
    )

    assert response.status_code == 200
    assert len(LOGIN_ATTEMPTS) == 1
    assert LOGIN_ATTEMPTS[0]["success"] is True
