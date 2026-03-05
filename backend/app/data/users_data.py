"""Simulated user database for registration"""

from typing import Dict, Any, Optional

_USERS: Dict[str, Dict[str, Any]] = {}
_CUSTOMERS: Dict[int, Dict[str, Any]] = {}
_MANAGERS: Dict[int, Dict[str, Any]] = {}
_DRIVERS: Dict[int, Dict[str, Any]] = {}

_NEXT_USER_ID = 1

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Return a user by email"""
    return _USERS.get(email)

def create_user(name: str, email: str, password_hash: str) -> Dict[str, Any]:
    """Create a new user"""
    global _NEXT_USER_ID  # pylint: disable=global-statement

    user = {
        "user_id": _NEXT_USER_ID,
        "name": name,
        "email": email,
        "password_hash": password_hash,
    }

    _USERS[email] = user
    _NEXT_USER_ID += 1

    return user

def create_customer(user_id: int, delivery_address: str = ""):
    """Create a customer profile"""
    _CUSTOMERS[user_id] = {
        "user_id": user_id,
        "delivery_address": delivery_address,
    }

def create_manager(user_id: int):
    """Create a manager profile"""
    _MANAGERS[user_id] = {
        "user_id": user_id,
        "manager_id": user_id,
    }

def create_driver(user_id: int, vehicle_type: str = "", is_available: bool = True):
    """Create a driver profile"""
    _DRIVERS[user_id] = {
        "user_id": user_id,
        "vehicle_type": vehicle_type,
        "is_available": is_available,
    }

def reset_users():
    """Reset the simulated user db"""
    global _USERS, _CUSTOMERS, _MANAGERS, _DRIVERS, _NEXT_USER_ID  # pylint: disable=global-statement
    _USERS = {}
    _CUSTOMERS = {}
    _MANAGERS = {}
    _DRIVERS = {}
    _NEXT_USER_ID = 1
