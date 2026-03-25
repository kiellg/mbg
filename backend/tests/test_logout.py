"""Tests for logout endpoint"""

from fastapi.testclient import TestClient

from main import app
from app.repositories.user_repo import reset_users
from app.repositories.session_repo import reset_session, get_session

client = TestClient(app)

def setup_function():
    """Reset data before each test"""
    reset_users()
    reset_session()

def register_and_login():
    """Register and log in a test user"""
    client.post(
        "/auth/register",
        json={
            "name": "Bob",
            "email": "bob@email.com",
            "password": "password123",
            "role": "customer",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "bob@email.com",
            "password": "password123",
        },
    )

    return login_response

def test_logout_ends_the_session():
    """Logging out should remove the active session"""
    login_response = register_and_login()

    session_token = login_response.cookies.get("session_token")

    assert session_token is not None
    assert get_session(session_token) is not None

    logout_response = client.post(
        "/auth/logout",
        cookies={
            "session_token": session_token,
        },
    )

    assert logout_response.status_code == 200
    assert logout_response.json() == {
        "message": "Logout successful",
    }
    assert get_session(session_token) is None

def test_logout_requires_login():
    """Logout should fail when no session cookie is provided"""
    response = client.post("/auth/logout")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Login required",
    }

def test_protected_route_requires_login_after_logout():
    """Protected route should reject access after logout"""
    login_response = register_and_login()

    session_token = login_response.cookies.get("session_token")

    protected_before_logout = client.get(
        "/auth/me",
        cookies={
            "session_token": session_token,
        },
    )

    assert protected_before_logout.status_code == 200
    assert "user_id" in protected_before_logout.json()

    logout_response = client.post(
        "/auth/logout",
        cookies={
            "session_token": session_token,
        },
    )

    assert logout_response.status_code == 200

    protected_before_logout = client.get(
        "/auth/me",
        cookies={
            "session_token": session_token,
        },
    )

    assert protected_before_logout.status_code == 401
    assert protected_before_logout.json() == {
        "detail": "Login required",
    }

def test_login_sets_session_cookie():
    """Login should create a session cookie"""
    login_response = register_and_login()

    session_token = login_response.cookies.get("session_token")

    assert login_response.status_code == 200
    assert session_token is not None
    assert get_session(session_token) is not None
