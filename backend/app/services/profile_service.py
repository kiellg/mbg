"""Service layer for profile update"""

from typing import Dict, Any, Optional
from fastapi import HTTPException

from backend.app.repositories import user_repo

def update_customer_profile(
        user_id: int,
        name: Optional[str],
        delivery_address: Optional[str],
) -> Dict[str, Any]:
    """Update customer profile fields"""
    if not user_repo.is_customer(user_id):
        raise HTTPException(status_code=403, detail="User is not a customer")

    user = user_repo.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if name is None and delivery_address is None:
        raise HTTPException(status_code=400, detail="No fields provided")

    if name is not None:
        user_repo.update_user_name(user_id, name)

    customer = user_repo.get_customer_by_user_id(user_id)

    return{
        "user_id": user_id,
        "name": user["name"],
        "delivery_address": customer["delivery_address"],
        "message": user_repo.get_customer_by_user_id(user_id),
    }
