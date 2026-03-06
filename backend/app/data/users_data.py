"""Simulated user database for registration"""

from datetime import datetime
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

def is_customer(user_id: int) -> bool:
    """Return whether a user is a customer"""
    return user_id in _CUSTOMERS

def is_manager(user_id: int) -> bool:
    """Return whether a user is a manager"""
    return user_id in _MANAGERS

def is_driver(user_id: int) -> bool:
    """Return whether a user is a driver"""
    return user_id in _DRIVERS

def get_user_role(user_id: int) -> Optional[str]:
    """Return the role for a user"""
    if is_customer(user_id):
        return "customer"
    
    if is_manager(user_id):
        return "manager"
    
    if is_driver(user_id):
        return "driver"
    
    return None

def increment_failed_login_attempts(email: str):
    """Increase failed login attempts for a user"""
    user = _USERS.get(email)

    if user:
        user["failed_login_attempts"] = user.get("failed_login_attempts", 0) + 1

def reset_failed_login_attempts(email: str):
    """Reset failed login attempts for a user"""
    user = _USERS.get(email)

    if not user:
        return 0
    
    return user.get("failed_login_attempts", 0)

def get_failed_login_attempts(email: str) -> int:
    """Return failed login attempts for a user"""
    user = _USERS.get(email)

    if not user:
        return 0
    
    return user.get("failed_login_attempts", 0)

def set_lock_until(email: str, lock_until: Optional[datetime]):
    """Set account lock time for a user"""
    user = _USERS.get(email)

    if user:
        user["lock_until"] = lock_until

def get_lock_until(email: str) -> Optional[datetime]:
    """Return account lock time for a user"""
    user = _USERS.get(email)

    if not user:
        return None
    
    return user.get("lock_until")

def reset_users():
    """Reset the simulated user db"""
    global _USERS, _CUSTOMERS, _MANAGERS, _DRIVERS, _NEXT_USER_ID  # pylint: disable=global-statement
    _USERS = {}
    _CUSTOMERS = {}
    _MANAGERS = {}
    _DRIVERS = {}
    _NEXT_USER_ID = 1
