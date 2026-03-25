"""Tests for customer profile update endpoint"""

from fastapi.testclient import TestClient

from main import app
from app.repositories.user_repo import(
    reset_users,
    create_user,
    create_customer,
)
from app.dependencies import get_current_user

client = TestClient(app)

def setup_function():
    """Reset database before each test"""
    reset_users()

def teardown_function():
    """Clear dependency overrides after each test"""
    app.dependency_overrides.clear()

def test_update_customer_profile_success():
    """Customer should be able to update profile fields"""

    user = create_user("Chris", "chris@email.com", "pass123")
    create_customer(user["user_id"], "123 Main Street")

    app.dependency_overrides[get_current_user] = lambda:{
        "user_id": user["user_id"]
    }

    response = client.patch(
        "/profile/customer",
        json={
            "name": "Chris Updated",
            "delivery_address": "456 West Street",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Chris Updated"
    assert data["delivery_address"] == "456 West Street"

def test_update_customer_profile_no_fields():
    """Empty update request should return error"""

    user = create_user("Chris", "chris@email.com", "pass123")
    create_customer(user["user_id"], "123 Main Street")

    app.dependency_overrides[get_current_user] = lambda:{
        "user_id": user["user_id"]
    }

    response = client.patch("/profile/customer", json={})

    assert response.status_code == 400
