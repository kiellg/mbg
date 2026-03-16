"""Repository layer for user data access"""

import uuid
import shortuuid
from datetime import datetime
from typing import Dict, Any, Optional

from backend.app.data import users_data

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Return a user by email"""
    return users_data.USERS.get(email)

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Return a user by user_id"""
    for user in users_data.USERS.values():
        if user["user_id"] == user_id:
            return user

    return None

def create_user(name: str, email: str, password_hash: str) -> Dict[str, Any]:
    """Create a new user"""
    user_id = str(uuid.uuid4())

    user = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "password_hash": password_hash,
    }

    users_data.USERS[email] = user

    return user

def create_customer(user_id: str, delivery_address: str = ""):
    """Create a customer profile"""
    users_data.CUSTOMERS[user_id] = {
        "user_id": user_id,
        "delivery_address": delivery_address,
    }

def create_manager(user_id: str):
    """Create a manager profile"""
    users_data.MANAGERS[user_id] = {
        "user_id": user_id,
        "manager_id": user_id,
    }

def create_driver(user_id: str, vehicle_type: str = "", is_available: bool = True):
    """Create a driver profile"""
    users_data.DRIVERS[user_id] = {
        "user_id": user_id,
        "vehicle_type": vehicle_type,
        "is_available": is_available,
    }

def is_customer(user_id: str) -> bool:
    """Return whether a user is a customer"""
    return user_id in users_data.CUSTOMERS

def is_manager(user_id: str) -> bool:
    """Return whether a user is a manager"""
    return user_id in users_data.MANAGERS

def is_driver(user_id: str) -> bool:
    """Return whether a user is a driver"""
    return user_id in users_data.DRIVERS

def get_user_role(user_id: str) -> Optional[str]:
    """Return the role for a user"""
    if is_customer(user_id):
        return "customer"

    if is_manager(user_id):
        return "manager"

    if is_driver(user_id):
        return "driver"

    return None

def get_customer_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Return a customer profile by user_id"""
    return users_data.CUSTOMERS.get(user_id)

def get_driver_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Return a driver profile by user_id"""
    return users_data.DRIVERS.get(user_id)

def update_user_name(user_id: str, name: str) -> Optional[Dict[str, Any]]:
    """Update the name of a user"""
    user = get_user_by_id(user_id)
    if not user:
        return None
    user["name"] = name
    return user

def update_customer_delivery_address(
        user_id: str,
        delivery_address: str,
) -> Optional[Dict[str, Any]]:
    """Update the delivery address of a customer"""
    customer = get_customer_by_user_id(user_id)
    if not customer:
        return None

    customer["delivery_address"] = delivery_address
    return customer

def increment_failed_login_attempts(email: str):
    """Increase failed login attempts for a user"""
    user = users_data.USERS.get(email)

    if user:
        user["failed_login_attempts"] = user.get("failed_login_attempts", 0) + 1

def reset_failed_login_attempts(email: str):
    """Reset failed login attempts for a user"""
    user = users_data.USERS.get(email)

    if user:
        user["failed_login_attempts"] = 0

def get_failed_login_attempts(email: str) -> int:
    """Return failed login attempts for a user"""
    user = users_data.USERS.get(email)

    if not user:
        return 0

    return user.get("failed_login_attempts", 0)

def set_lock_until(email: str, lock_until: Optional[datetime]):
    """Set account lock time for a user"""
    user = users_data.USERS.get(email)

    if user:
        user["lock_until"] = lock_until

def get_lock_until(email: str) -> Optional[datetime]:
    """Return account lock time for a user"""
    user = users_data.USERS.get(email)

    if not user:
        return None

    return user.get("lock_until")

def store_password_reset_token(
        token: str,
        user_id: str,
        expires_at: datetime,
) -> None:
    """Store a password reset token"""
    users_data.PASSWORD_RESET_TOKENS[token] = {
        "user_id": user_id,
        "expires_at": expires_at
    }

def get_password_reset_token(token: str) -> Optional[Dict[str, Any]]:
    """Return a password reset token"""
    return users_data.PASSWORD_RESET_TOKENS.get(token)

def delete_password_reset_token(token: str) -> None:
    """Delete a password reset token"""
    users_data.PASSWORD_RESET_TOKENS.pop(token, None)

def reset_users():
    """Reset the simulated user db"""
    users_data.USERS.clear()
    users_data.CUSTOMERS.clear()
    users_data.MANAGERS.clear()
    users_data.DRIVERS.clear()

def save_payment_method(
        customer_id: str,
        card_token: str,
        last4: str,
        expiry_date: str,
        cardholder_name: str,
        nickname: None,
):
    """Save a tokenized payment method to the customer profile."""
    customer = users_data.CUSTOMERS.get(customer_id)
    if customer is None:
        return None
    
    method = {
        "saved_method_id": shortuuid.ShortUUID().random(length=7),
        "card_token": card_token,
        "last4": last4,
        "expiry_date": expiry_date,
        "cardholder_name": cardholder_name,
        "nickname": nickname,
    }

    if "saved_payment_methods" not in customer:
        customer["saved_payment_methods"] = []
    
    customer["saved_payment_methods"].append(method)
    return method

def get_saved_payment_methods(customer_id: str):
    """Return all saved payment methods for a customer"""
    customer = users_data.CUSTOMERS.get(customer_id)
    if customer is None:
        return []
    return customer.get("saved_payment_methods", [])
