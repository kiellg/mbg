#pylint: disable=protected-access
"""Unit tests for admin_service profile management"""
from datetime import datetime, timezone
import pytest
from fastapi import HTTPException

from app.data import users_data, restaurants_data, order_data, session_store
from app.repositories import user_repo
from app.services import admin_service, get_order_analytics

@pytest.fixture(autouse=True)
def reset_state():
    """Reset user data before and after each test"""
    user_repo.reset_users()
    order_data._ORDERDB.clear()
    yield
    user_repo.reset_users()
    order_data._ORDERDB.clear()

def _add_customer(user_id="cust-1", email="cust@test.com"):
    """Helper to add a customer user for testing"""
    users_data.USERS[email] = {
        "user_id": user_id,
        "name": "Test Customer",
        "email": email,
        "password_hash": "hash",
    }
    users_data.CUSTOMERS[user_id] = {"user_id": user_id}

def test_list_all_profiles_returns_profile_response_shape():
    """Service should return dicts matching ProfileResponse schema"""
    profiles = admin_service.list_all_profiles()
    for p in profiles:
        assert "user_id" in p
        assert "name" in p
        assert "email" in p
        assert "role" in p
        assert "password_hash" not in p

def test_list_all_profiles_includes_seeded_admin():
    """Seeded admin user should be included in profile list with correct role"""
    profiles = admin_service.list_all_profiles()
    admin = next((p for p in profiles if p["user_id"] == users_data.SEEDED_ADMIN_USER_ID), None)
    assert admin is not None
    assert admin["role"] == "admin"

def test_delete_user_removes_customer():
    """Deleting a customer user should remove them from the data store"""
    _add_customer()
    admin_service.delete_user("cust-1")
    assert "cust@test.com" not in users_data.USERS

def test_delete_user_raises_403_for_admin():
    """Attempting to delete an admin user should raise a 403 HTTPException"""
    with pytest.raises(HTTPException) as exc_info:
        admin_service.delete_user(users_data.SEEDED_ADMIN_USER_ID)
    assert exc_info.value.status_code == 403

def test_delete_user_raises_404_for_nonexistent():
    """Attempting to delete a non-existent user should raise a 404 HTTPException"""
    with pytest.raises(HTTPException) as exc_info:
        admin_service.delete_user("ghost-id")
    assert exc_info.value.status_code == 404

def test_delete_user_revokes_sessions():
    """Deleting a user should invalidate their active sessions"""
    _add_customer()
    session_store.SESSIONS["tok-123"] = {"user_id": "cust-1"}
    admin_service.delete_user("cust-1")
    assert "tok-123" not in session_store.SESSIONS

def test_delete_user_clears_owner_reference():
    """Deleting a manager should clear owner_id on their restaurants"""
    restaurants_data._DB[99] = {"id": 99, "owner_id": "cust-1", "menu": []}
    _add_customer()
    admin_service.delete_user("cust-1")
    assert restaurants_data._DB[99]["owner_id"] is None

def test_delete_user_clears_driver_reference():
    """Deleting a driver should clear driver_id on their assigned orders"""
    order_data._ORDERDB["o1"] = {"order_id": "o1", "driver_id": "cust-1"}
    _add_customer()
    admin_service.delete_user("cust-1")
    assert order_data._ORDERDB["o1"]["driver_id"] == ""

def _seed_order(order_id: str, status: str = "Delivered"):
    order_data._ORDERDB[order_id] = {
        "order_id": order_id,
        "customer_id": "cust-1",
        "restaurant_id": 1,
        "status": status,
        "created_at": datetime.now(timezone.utc),
        "total": "20.00",
    }


def test_get_order_analytics_returns_correct_total():
    """total_orders should reflect the number of seeded orders."""
    _seed_order("o-1")
    _seed_order("o-2")
    result = get_order_analytics()
    assert result["total_orders"] >= 2


def test_get_order_analytics_counts_by_status():
    """orders_by_status should correctly group orders by their status."""
    _seed_order("o-pending", status="Pending")
    _seed_order("o-delivered", status="Delivered")
    result = get_order_analytics()
    assert result["orders_by_status"]["Pending"] >= 1
    assert result["orders_by_status"]["Delivered"] >= 1


def test_get_order_analytics_counts_orders_today():
    """Orders created today should appear in orders_today."""
    _seed_order("o-today")
    result = get_order_analytics()
    assert result["orders_today"] >= 1


def test_get_order_analytics_counts_orders_this_week():
    """Orders created today should appear in orders_this_week."""
    _seed_order("o-week")
    result = get_order_analytics()
    assert result["orders_this_week"] >= 1


def test_get_order_analytics_empty_db():
    """Analytics on empty order DB should return zeros."""
    order_data._ORDERDB.clear()
    result = get_order_analytics()
    assert result["total_orders"] == 0
    assert result["orders_today"] == 0
    assert result["orders_this_week"] == 0
    assert not result["orders_by_status"]
