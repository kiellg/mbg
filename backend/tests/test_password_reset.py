"""Tests for password reset functionality"""

from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from backend.main import app
from backend.app.data import users_data
from backend.app.repositories.user_repo import create_user, reset_users
from backend.app.services.auth_service import hash_password

client = TestClient(app)

def setup_function():
    """Reset db before each test"""
    reset_users()

def test_request_password_reset_success():
    """User can request a password reset"""
    create_user("test", "test@email.com", hash_password("pw123"))

    response = client.post(
        "/auth/forgot-password",
        json={"email": "test@email.com"},
    )

    assert response.status_code == 200
    assert "reset_token" in response.json()

def test_request_password_reset_invalid_email():
    """Reset request should fail if email doesn't exist"""
    response = client.post(
        "/auth/forgot-password",
        json={"email": "invalid@email.com"},
    )

    assert response.status_code == 404

def test_reset_password_success():
    """User can reset password using token"""
    create_user("test", "test@email.com", hash_password("pw123"))

    token_response = client.post(
        "/auth/forgot-password",
        json={"email": "test@email.com"},
    )

    token = token_response.json()["reset_token"]

    response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": "newpass123",
        },
    )

    assert response.status_code == 200

def test_reset_password_invalid_token():
    """Reset should fail for invalid token"""
    response = client.post(
        "/auth/reset-password",
        json={
            "token": "invalidtoken",
            "new_password": "newpass123",
        },
    )

    assert response.status_code == 400

def test_reset_password_expired_token():
    """Reset should fail if token is expired"""
    create_user("test", "test@email.com", hash_password("pw123"))

    token_response = client.post(
        "/auth/forgot-password",
        json={"email": "test@email.com"},
    )

    token = token_response.json()["reset_token"]

    users_data.PASSWORD_RESET_TOKENS[token]["expires_at"] = (
        datetime.now() - timedelta(hours=2)
    )

    response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": "newpass123",
        },
    )

    assert response.status_code == 400
