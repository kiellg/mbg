"""Tests for driver role permissions"""
# pylint: disable=duplicate-code

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
    """Reset data before each test"""
    reset_users()
    reset_session()

def create_driver_session():
    """Create a session token for a driver user"""
    user = create_user("driv", "driv@test.com", "pw123")
    create_driver(user["user_id"])
    return create_session(user["user_id"])

def create_customer_session():
    """Create a session token for a customer user"""
    user = create_user("cust", "cust@test.com", "pw123")
    create_customer(user["user_id"])
    return create_session(user["user_id"])

def create_manager_session():
    """Create a session token for a manager user"""
    user = create_user("mgr", "mgr@test.com", "pw123")
    create_manager(user["user_id"])
    return create_session(user["user_id"])

def test_driver_can_view_assigned_deliveries():
    """Drivers should be able to view assigned deliveries"""
    token = create_driver_session()

    response = client.get(
        "/orders/assigned",
        headers={"session-token": token},
    )

    assert response.status_code == 200

def test_driver_can_update_delivery_status():
    """Driver should be able to update delivery status"""
    token = create_driver_session()

    response = client.patch(
        "/orders/1/status",
        headers={"session-token": token},
    )

    assert response.status_code == 200

def test_customer_cannot_view_assigned_deliveries():
    """Customer should not be allowed to view driver deliveries"""
    token = create_customer_session()

    response = client.get(
        "/orders/assigned",
        headers={"session-token": token},
    )

    assert response.status_code == 403

def test_manager_cannot_update_delivery_status():
    """Manager should not be allowed to update delivery status"""
    token = create_manager_session()

    response = client.patch(
        "/orders/1/status",
        headers={"session-token": token},
    )

    assert response.status_code == 403
