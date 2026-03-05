"""Tests for the user registration endpoint"""

from fastapi.testclient import TestClient
from backend.main import app
from backend.app.data.users_data import reset_users

client = TestClient(app)

def setup_function():
    """Reset db before each test"""
    reset_users()

def test_register_customer():
    """Registering a user should succeed"""
    response = client.post(
        "/auth/register",
        json={
            "name": "John",
            "email": "john@test.com",
            "password": "password123",
            "role": "customer",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "john@test.com"
    assert "user_id" in data
    