"""Tests for manager restaurant profile update endpoint"""

from fastapi.testclient import TestClient

from backend.main import app
from backend.app.repositories.user_repo import(
    reset_users,
    create_user,
    create_manager,
)
from backend.app.repositories.restaurant_repo import get_restaurant_record
from backend.app.dependencies import get_current_user

client = TestClient(app)

def setup_function():
    """Reset db before each test"""
    reset_users()

def teardown_function():
    """Clear dependency override"""
    app.dependency_overrides.clear()

def test_manager_can_update_restaurant_profile():
    """Manager should be able to update restaurant fields"""

    user = create_user("mgr", "mgr@email.com", "pw123")
    create_manager(user["user_id"])

    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": user["user_id"]
    }

    response = client.patch(
        "/profile/restaurant/1",
        json={
            "name": "Updated Restaurant",
            "address": "New Address",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Restaurant"
    assert data["address"] == "New Address"

def test_manager_update_restaurant_no_fields():
    """Empty request should return error"""

    user = create_user("mgr", "mgr@email.com", "pw123")
    create_manager(user["user_id"])

    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": user["user_id"]
    }

    response = client.patch("/profile/restaurant/1", json={})

    assert response.status_code == 400

def test_non_manager_cannot_update_restaurant():
    """Non manager users should not be allowed to update restaurant profiles"""

    user = create_user("cust", "cust@email.com", "pw123")

    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": user["user_id"]
    }

    response = client.patch(
        "/profile/restaurant/1",
        json={"name": "New name"},
    )

    assert response.status_code == 403

def test_manager_cannot_update_other_restaurant():
    """Manager can't update restaurant they do not own"""

    mgr1 = create_user("mgr1", "mgr1@email.com", "pw123")
    create_manager(mgr1["user_id"])

    mgr2 = create_user("mgr2", "mgr2@email.com", "pw123")
    create_manager(mgr2["user_id"])

    restaurant = get_restaurant_record(1)
    restaurant["owner_id"] = mgr1["user_id"]

    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": mgr2["user_id"]
    }

    response = client.patch(
        "/profile/restaurant/1",
        json={"name": "Illegal update"}
    )

    assert response.status_code == 403
