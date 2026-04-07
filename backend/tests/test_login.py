"""Tests for the user login endpoint"""

from fastapi.testclient import TestClient

from main import app
from app.data.users_data import SEEDED_ADMIN_EMAIL, SEEDED_ADMIN_PASSWORD
from app.repositories.user_repo import(
    reset_users,
    create_user,
    create_customer,
)
from app.repositories.session_repo import reset_session
from app.services.auth_service import hash_password

client = TestClient(app)

def setup_function():
    """Reset db before each test"""
    reset_users()
    reset_session()

def test_login_success():
    """Logging in with valid credentials should succeed"""
    user = create_user("John", "john@example.com", hash_password("password123"))
    create_customer(user["user_id"])

    response = client.post(
        "/auth/login",
        json={
            "email": "john@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful!"
    assert response.json()["user_id"] == user["user_id"]
    assert response.json()["email"] == "john@example.com"
    assert response.json()["role"] == "customer"
    assert "session_token" in response.cookies

def test_login_invalid_password():
    """Logging in with wrong password should fail"""
    user = create_user("John", "john@example.com", hash_password("password123"))
    create_customer(user["user_id"])

    response = client.post(
        "/auth/login",
        json={
            "email": "john@example.com",
            "password": "wrongpass",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_invalid_email():
    """Logging in with unknown email should fail"""
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_seeded_admin_can_login():
    """The seeded internal admin should be able to authenticate normally."""
    response = client.post(
        "/auth/login",
        json={
            "email": SEEDED_ADMIN_EMAIL,
            "password": SEEDED_ADMIN_PASSWORD,
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == SEEDED_ADMIN_EMAIL
    assert response.json()["role"] == "admin"
    assert "session_token" in response.cookies

def test_login_locks_after_five_failed_attempts():
    """Account should lock after five failed login attempts"""
    user = create_user("John", "john@example.com", hash_password("password123"))
    create_customer(user["user_id"])

    for _ in range(5):
        response = client.post(
            "/auth/login",
            json={
                "email": "john@example.com",
                "password": "wrongpass",
            },
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Account is locked. Please try again later."

def test_locked_account_cant_login():
    """Locked account should not allow login even with correct password"""
    user = create_user("John", "john@example.com", hash_password("password123"))
    create_customer(user["user_id"])

    for _ in range(5):
        response = client.post(
            "/auth/login",
            json={
                "email": "john@example.com",
                "password": "wrongpass",
            },
        )

    response = client.post(
        "/auth/login",
        json={
            "email": "john@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Account is locked. Please try again later."
