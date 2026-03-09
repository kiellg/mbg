"""Tests for restaurant role permissions"""

from fastapi.testclient import TestClient

from backend.main import app
from backend.app.repositories.session_repo import create_session, reset_session
from backend.app.repositories.user_repo import(
    create_user,
    create_customer,
    create_manager,
    create_driver,
    reset_users,
)

client = TestClient(app)

def setup_function():
    reset_users()
    reset_session()

def create_customer_session():
    user = create_user("cust", "cust@test.com", "pw123")
    create_customer(user["user_id"])
    return create_session(user["user_id"])

def create_manager_session():
    user = create_user("mgr", "mgr@test.com", "pw123")
    create_manager(user["user_id"])
    return create_session(user["user_id"])

def create_driver_session():
    user = create_user("driv", "driv@test.com", "pw123")
    create_driver(user["user_id"])
    return create_session(user["user_id"])

def test_customer_can_view_menu():
    token = create_customer_session()
    response = client.get("/restaurants/1/menu", headers={"session-token": token})
    assert response.status_code == 200

def test_customer_cannot_create_menu():
    token = create_customer_session()
    response = client.post(
        "/restaurants/1/menu",
        headers={"session-token": token},
        json={
            "name": "Burger",
            "description": "Beef burger",
            "dietary_tag": "",
            "price_cents": 1000,
            "is_visible": True,
            "is_active": True,
            "is_available": True,
            "category_id": 1,
        },
    )
    assert response.status_code == 403

def test_manager_can_create_menu():
    token = create_manager_session()
    response = client.post(
        "/restaurants/1/menu",
        headers={"session-token": token},
        json={
            "name": "Pizza",
            "description": "Cheese pizza",
            "dietary_tag": "",
            "price_cents": 2000,
            "is_visible": True,
            "is_active": True,
            "is_available": True,
            "category_id": 1,
        },
    )
    assert response.status_code == 201

def test_drive_cannot_delete_restaurants():
    token = create_driver_session()
    response = client.delete("/restaurants/1", headers={"session-token": token})
    assert response.status_code == 403
