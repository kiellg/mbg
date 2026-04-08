"""Router for user endpoints"""
from typing import Optional
from fastapi import APIRouter, Header

from app.services.role_service import require_manager
from app.repositories import user_repo

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/drivers")
def get_drivers(
    delivery_method: Optional[str] = None,
    session_token: Optional[str] = Header(default=None),
):
    """Get all drivers, optionally filtered by delivery method (manager only)"""
    require_manager(session_token)
    
    drivers = []
    for user_id, driver_data in user_repo.users_data.DRIVERS.items():
        user = user_repo.get_user_by_id(user_id)
        if user:
            driver_info = {
                "user_id": user_id,
                "name": user.get("name", "Unknown"),
                "delivery_method": driver_data.get("delivery_method"),
                "is_available": driver_data.get("is_available", True),
            }
            
            # Filter by delivery_method if provided
            if delivery_method is None or driver_info["delivery_method"] == delivery_method:
                drivers.append(driver_info)
    
    return drivers
