"""Tests for driver profile update endpoint"""

from fastapi.testclient import TestClient

from backend.main import app
from backend.app.repositories.user_repo import(
    reset_users,
    create_user,
    create_driver,
)
from backend.app.dependencies import get_current_user

client = TestClient(app)

def setup_function():
    """Reset db before each test"""
    reset_users()

def teardown_function():
    """Clear dependency overrides"""
    app.dependency_overrides.clear()

def test_driver_can_update_profile():
    """Driver should be able to update profile fields"""

    user = create_user("driv", "driv@email.com", "pw123")
    create_driver(user["user_id"], "car", True)

    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": user["user_id"]
    }

    response = client.patch(
        "/profile/driver",
        json={
            "name": "Updated Driver",
            "vehicle_type": "bike",
            "is_available": False
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Driver"
    assert data["vehicle_type"] == "bike"
    assert data["is_available"] is False

def test_driver_update_no_fields():
    """Empty update request should return error"""

    user = create_user("driv", "driv@email.com", "pw123")
    create_driver(user["user_id"], "car", True)

    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": user["user_id"]
    }

    response = client.patch("/profile/driver", json={})

    assert response.status_code == 400
