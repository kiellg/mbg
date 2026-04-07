"""Tests for role based access service"""

import pytest
from fastapi import HTTPException

from app.repositories.session_repo import create_session, reset_session

from app.repositories.user_repo import(
    create_user,
    create_admin,
    create_customer,
    create_manager,
    create_driver,
    reset_users,
)

from app.services.role_service import(
    require_role,
    require_admin,
    require_customer,
    require_manager,
    require_driver,
)

def setup_function():
    """Reset data before each test"""
    reset_users()
    reset_session()

def create_customer_session() -> str:
    """Create a session for a customer"""
    user = create_user("Yohanes", "yohanes@email.com", "pass123")
    create_customer(user["user_id"])
    return create_session(user["user_id"])

def create_admin_session() -> str:
    """Create a session for an admin"""
    user = create_user("Admin", "admin@email.com", "pass123")
    create_admin(user["user_id"])
    return create_session(user["user_id"])

def create_manager_session() -> str:
    """Create a session for a manager"""
    user = create_user("Edgar", "edgar@email.com", "pass123")
    create_manager(user["user_id"])
    return create_session(user["user_id"])

def create_driver_session() -> str:
    """Create a session for a driver"""
    user = create_user("Kiel", "kiel@email.com", "pass123")
    create_driver(user["user_id"])
    return create_session(user["user_id"])

def test_require_role_allows_manager():
    """Allowed role should pass authorization"""
    session_token = create_manager_session()

    session = require_role(session_token, ["manager"])

    assert isinstance(session, dict)
    assert "user_id" in session

def test_require_role_blocks_customer():
    """Unauthorized role should raise forbidden error"""
    session_token = create_customer_session()

    with pytest.raises(HTTPException) as exc_info:
        require_role(session_token, ["manager"])

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Access denied"

def test_require_role_invalid_session():
    """Invalid session should raise unauthorized error"""
    with pytest.raises(HTTPException) as exc_info:
        require_role("Invalid", ["manager"])

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Login required"

def test_require_customer_allows_customer():
    """Customer helper should allow customers"""
    session_token = create_customer_session()

    session = require_customer(session_token)

    assert isinstance(session, dict)
    assert "user_id" in session

def test_require_admin_allows_admin():
    """Admin helper should allow admins"""
    session_token = create_admin_session()

    session = require_admin(session_token)

    assert isinstance(session, dict)
    assert "user_id" in session

def test_require_manager_allows_manager():
    """Manager helper should allow managers"""
    session_token = create_manager_session()

    session = require_manager(session_token)

    assert isinstance(session, dict)
    assert "user_id" in session

def test_require_driver_allows_driver():
    """Driver helper should allow drivers"""
    session_token = create_driver_session()

    session = require_driver(session_token)

    assert isinstance(session, dict)
    assert "user_id" in session

def test_driver_blocked_from_manager_access():
    """Driver shouldn't pass manager authorization"""
    session_token = create_driver_session()

    with pytest.raises(HTTPException) as exc_info:
        require_manager(session_token)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Access denied"


def test_manager_blocked_from_admin_access():
    """Manager shouldn't pass admin authorization"""
    session_token = create_manager_session()

    with pytest.raises(HTTPException) as exc_info:
        require_admin(session_token)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Access denied"
