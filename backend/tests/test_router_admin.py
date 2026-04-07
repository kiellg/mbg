"""Integration tests for admin user profile management endpoints"""
import pytest
from fastapi.testclient import TestClient

from app.data import users_data
from app.repositories import user_repo
from app.data import order_data
from main import app

client = TestClient(app)

ADMIN_EMAIL = users_data.SEEDED_ADMIN_EMAIL
ADMIN_PASSWORD = users_data.SEEDED_ADMIN_PASSWORD

@pytest.fixture(autouse=True)
def reset_state():
    """Reset user stores before each test"""
    user_repo.reset_users()
    client.cookies.clear()
    order_data._ORDERDB.clear()
    yield
    user_repo.reset_users()
    client.cookies.clear()
    order_data._ORDERDB.clear()

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
    response = client.post("/auth/register", json={
        "name": "Test Customer",
        "email": email,
        "password": password,
        "role": "customer",
    })
    assert response.status_code in (200, 201), f"Registration failed: {response.json()}"

def test_list_profiles_returns_all_users():
    """Admin should be able to list all user profiles with role and no sensitive fields"""
    _register_customer()
    token = _get_admin_token()
    response = client.get("/admin/users", cookies={"session_token": token})
    assert response.status_code == 200
    assert len(response.json()) >= 2
    for profile in response.json():
        assert "role" in profile
        assert "password_hash" not in profile

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

    profiles_after = client.get("/admin/users", cookies={"session_token": token}).json()
    assert not any(p["user_id"] == customer["user_id"] for p in profiles_after)

    repeat_response = client.delete(
        f"/admin/users/{customer['user_id']}",
        cookies={"session_token": token},
    )
    assert repeat_response.status_code == 404

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

def test_list_users_requires_authentication():
    """GET /admin/users should return 401 when no session token is provided"""
    response = client.get("/admin/users")
    assert response.status_code == 401

def test_delete_user_requires_authentication():
    """DELETE /admin/users/{id} should return 401 when no session token is provided"""
    response = client.delete("/admin/users/some-user-id")
    assert response.status_code == 401

from app.data import order_data
from app.repositories import order_repo
from datetime import datetime, timezone


def _seed_order(order_id: str, status: str = "Delivered"):
    """Seed a fake order directly into the order DB."""
    order_data._ORDERDB[order_id] = {
        "order_id": order_id,
        "customer_id": "cust-1",
        "restaurant_id": 1,
        "status": status,
        "created_at": datetime.now(timezone.utc),
        "total": "20.00",
    }


def test_get_order_analytics_returns_200():
    """Admin should be able to get order analytics."""
    token = _get_admin_token()
    response = client.get("/admin/analytics/orders", cookies={"session_token": token})
    assert response.status_code == 200


def test_get_order_analytics_returns_correct_shape():
    """Analytics response should contain expected fields."""
    token = _get_admin_token()
    response = client.get("/admin/analytics/orders", cookies={"session_token": token})
    data = response.json()
    assert "total_orders" in data
    assert "orders_today" in data
    assert "orders_this_week" in data
    assert "orders_by_status" in data


def test_get_order_analytics_counts_todays_orders():
    """Orders created today should be reflected in orders_today."""
    _seed_order("order-today", status="Delivered")
    token = _get_admin_token()
    response = client.get("/admin/analytics/orders", cookies={"session_token": token})
    assert response.json()["orders_today"] >= 1


def test_get_order_analytics_requires_authentication():
    """GET /admin/analytics/orders should return 401 with no token."""
    response = client.get("/admin/analytics/orders")
    assert response.status_code == 401


def test_get_order_analytics_requires_admin_role():
    """Non-admin users should not be able to access analytics."""
    _register_customer()
    token = _get_customer_token()
    response = client.get("/admin/analytics/orders", cookies={"session_token": token})
    assert response.status_code == 403
