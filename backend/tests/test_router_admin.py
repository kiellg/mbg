"""Integration tests for admin user profile management endpoints"""
import pytest
from fastapi.testclient import TestClient

from app.data import users_data
from app.repositories import user_repo
from main import app

client = TestClient(app)

ADMIN_EMAIL = users_data.SEEDED_ADMIN_EMAIL
ADMIN_PASSWORD = users_data.SEEDED_ADMIN_PASSWORD

@pytest.fixture(autouse=True)
def reset_state():
    """Reset user stores before each test"""
    user_repo.reset_users()
    yield
    user_repo.reset_users()

def _get_admin_token() -> str:
    """Log in as the seeded admin and return a session token from the cookie"""
    response = client.post("/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
    })
    assert response.status_code == 200
    return response.cookies["session_token"]

def _get_customer_token(email="cust@test.com", password="pass123") -> str:
    """Log in as a customer and return a session token from the cookie"""
    response = client.post("/auth/login", json={
        "email": email,
        "password": password,
    })
    assert response.status_code == 200
    return response.cookies["session_token"]

def _register_customer(email="cust@test.com", password="pass123"):
    """Register a new customer user for testing"""
    client.post("/auth/register", json={
        "name": "Test Customer",
        "email": email,
        "password": password,
        "role": "customer",
    })

def test_list_profiles_returns_all_users():
    """Admin should be able to list all user profiles"""
    _register_customer()
    token = _get_admin_token()
    response = client.get("/admin/users", cookies={"session_token": token})
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_list_profiles_includes_role():
    """Each profile in the list should include a resolved role"""
    token = _get_admin_token()
    response = client.get("/admin/users", cookies={"session_token": token})
    for profile in response.json():
        assert "role" in profile

def test_list_profiles_requires_admin_role():
    """Non-admin users should not be able to list profiles"""
    _register_customer()
    token = _get_customer_token()
    response = client.get("/admin/users", cookies={"session_token": token})
    assert response.status_code == 403

def test_delete_user_removes_profile():
    """Admin should be able to delete a user profile"""
    _register_customer()
    token = _get_admin_token()
    profiles = client.get("/admin/users", cookies={"session_token": token}).json()
    customer = next(p for p in profiles if p["email"] == "cust@test.com")
    response = client.delete(
        f"/admin/users/{customer['user_id']}",
        cookies={"session_token": token},
    )
    assert response.status_code == 204

def test_delete_user_returns_404_for_nonexistent_user():
    """Deleting a nonexistent user should return 404"""
    token = _get_admin_token()
    response = client.delete("/admin/users/nonexistent-id", cookies={"session_token": token})
    assert response.status_code == 404

def test_delete_user_requires_admin_role():
    """Non-admin users should not be able to delete profiles."""
    _register_customer()
    token = _get_customer_token()
    response = client.delete("/admin/users/some-id", cookies={"session_token": token})
    assert response.status_code == 403

def test_delete_user_cannot_delete_admin():
    """Admin accounts should not be deletable"""
    token = _get_admin_token()
    response = client.delete(
        f"/admin/users/{users_data.SEEDED_ADMIN_USER_ID}",
        cookies={"session_token": token},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin accounts cannot be deleted."
