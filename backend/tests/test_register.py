"""Tests for the user registration endpoint"""

from fastapi.testclient import TestClient
from backend.main import app
from backend.app.repositories.user_repo import reset_users

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

def test_register_duplicate_email():
    """Registering with a duplicate email should fail"""

    # first registration
    client.post(
        "/auth/register",
        json={
            "name": "John",
            "email": "john@test.com",
            "password": "password123",
            "role": "customer",
        },
    )

    # second registration with same email
    response = client.post(
        "/auth/register",
        json={
            "name": "Jane",
            "email": "john@test.com",
            "password": "password123",
            "role": "customer",
        },
    )

    assert response.status_code == 400

def test_register_invalid_email():
    """Registering with an invalid email format should fail"""

    response = client.post(
        "/auth/register",
        json={
            "name": "John",
            "email": "not_email",
            "password": "password123",
            "role": "customer",
        },
    )

    assert response.status_code == 422
