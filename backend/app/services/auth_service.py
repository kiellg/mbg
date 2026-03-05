"""Service layer containing business logic for user registration"""

import hashlib
from fastapi import HTTPException

from app.data.users_data import(
    get_user_by_email,
    create_user,
    create_customer,
    create_manager,
    create_driver,
)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name: str, email: str, password: str, role: str):
    if get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    password_hash = hash_password(password)

    user = create_user(name, email, password_hash)

    if role == "customer":
        create_customer(user["user_id"])

    elif role == "manager":
        create_manager(user["user_id"])

    elif role == "driver":
        create_driver(user["user_id"])

    return user
