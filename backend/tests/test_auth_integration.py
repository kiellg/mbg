"""Integration tests for authentication flow"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def register_and_login(email="test@email.com"):
    """Helper to register and login user"""
    reg = client.post("/auth/register", json={
        "name": "test user",
        "email": email,
        "password": "pass123",
        "role": "customer",
    })
    assert reg.status_code == 200

    response = client.post("/auth/login", json={
        "email": email,
        "password": "pass123",
    })
    assert response.status_code == 200

    return response.cookies

def test_auth_full_flow():
    """Register -> login -> access -> logout"""

    # Register
    response = client.post("/auth/register", json={
        "name": "test user 2",
        "email": "test2@email.com",
        "password": "pass123",
        "role": "customer",
    })
    assert response.status_code == 200

    # Login
    response = client.post("/auth/login", json={
        "email": "test2@email.com",
        "password": "pass123",
    })
    assert response.status_code == 200

    cookies = response.cookies
    assert "session_token" in cookies

    # Access protected route
    response = client.get("/auth/me", cookies=cookies)
    assert response.status_code == 200
    assert "user_id" in response.json()

    # Logout
    response = client.post("/auth/logout", cookies=cookies)
    assert response.status_code == 200

def test_login_required_for_protected_routes():
    """Should block access without login"""
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_logout_without_session():
    """Logout should fail without cookie"""
    response = client.post("/auth/logout")
    assert response.status_code == 401

def test_profile_update_customer():
    """Login -> update profile"""
    cookies = register_and_login("test3@email.com")

    response = client.patch(
        "/profile/customer",
        json={
            "name": "Updated name",
            "delivery_address": "67 Main St",
        },
        cookies=cookies,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated name"
