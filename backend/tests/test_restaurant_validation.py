"""Tests for restaurant and menu item validation and deletion"""
#pylint: disable=no-value-for-parameter
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app
from app.services.restaurants_service import delete_restaurant_by_id
from app.repositories.session_repo import create_session, reset_session
from app.repositories.user_repo import(
    create_manager,
    create_user,
    reset_users,
)

client = TestClient(app)

def setup_function():
    """Reset data before each test"""
    reset_users()
    reset_session()

def create_manager_session():
    """Create s session for a manager"""
    user = create_user("mgr", "mgr@test.com", "pw123")
    create_manager(user["user_id"])
    return create_session(user["user_id"])

# Unit tests for the service layer validation logic
def test_negative_price_rejected_by_schema():
    """Pydantic should reject negative price_cents with 422"""
    response = client.post(
        "/restaurants/1/menu",
        json={"name": "Burger", "price_cents": -100, "category_id": 10},
    )
    assert response.status_code == 422

def test_missing_name_rejected_by_schema():
    """Pydantic should reject empty name with 422"""
    response = client.post(
        "/restaurants/1/menu",
        json={"name": "", "price_cents": 999, "category_id": 10},
    )
    assert response.status_code == 422

def test_service_blocks_deletion_with_active_items():
    """Delete restaurant with active menu items should raise 400"""
    with pytest.raises(HTTPException) as exc:
        delete_restaurant_by_id(1)
    assert exc.value.status_code == 400
    assert "active menu items" in exc.value.detail

# Integration tests for the API endpoints
def test_delete_restaurant_with_active_items_returns_400():
    """DELETE /restaurants/1 should fail if active menu items exist"""
    token = create_manager_session()

    response = client.delete(
        "/restaurants/1",
        headers={"session-token": token},
    )
    assert response.status_code == 400

def test_delete_nonexistent_restaurant_returns_404():
    """DELETE /restaurants/999 should return 404"""
    token = create_manager_session()

    response = client.delete(
        "/restaurants/999",
        headers={"session-token": token},
    )
    assert response.status_code == 404
