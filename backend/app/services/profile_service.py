"""Service layer for profile update"""

from typing import Dict, Any
from fastapi import HTTPException

from app.repositories import user_repo, restaurant_repo

def update_customer_profile(user_id, name, delivery_address) -> Dict[str, Any]:
    """Update customer profile fields"""
    user = user_repo.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user_repo.is_customer(user_id):
        raise HTTPException(status_code=403, detail="User is not a customer")

    if name is None and delivery_address is None:
        raise HTTPException(status_code=400, detail="No fields provided")

    if name is not None:
        user_repo.update_user_name(user_id, name)

    if delivery_address is not None:
        user_repo.update_customer_delivery_address(user_id, delivery_address)

    customer = user_repo.get_customer_by_user_id(user_id)

    return{
        "user_id": user_id,
        "name": user["name"],
        "delivery_address": customer["delivery_address"],
        "message": "Customer profile updated successfully",
    }

def update_manager_restaurant_profile(
        user_id: int,
        restaurant_id: int,
        request,
):
    """Update restaurant profile information for a manager"""

    restaurant = restaurant_repo.get_restaurant_record(restaurant_id)
    owner_id = restaurant.get("owner_id")

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    if not user_repo.is_manager(user_id):
        raise HTTPException(status_code=403, detail="User is not a manager")

    if owner_id is not None and owner_id != user_id:
        raise HTTPException(status_code=403, detail="Manager does not own this restaurant")

    if(
        request.name is None
        and request.address is None
        and request.rating is None
        and request.opening_hours is None
    ):
        raise HTTPException(status_code=400, detail="No fields provided")

    patch ={}

    if request.name is not None:
        patch["name"] = request.name

    if request.address is not None:
        patch["address"] = request.address

    if request.rating is not None:
        patch["rating"] = request.rating

    if request.opening_hours is not None:
        patch["opening_hours"] = request.opening_hours

    restaurant_repo.update_restaurant(restaurant_id, patch)

    updated = restaurant_repo.get_restaurant_record(restaurant_id)

    return{
        "restaurant_id": restaurant_id,
        "name": updated["name"],
        "address": updated["address"],
        "rating": updated["rating"],
        "opening_hours": updated["opening_hours"],
        "message": "Restaurant profile updated successfully",
    }

def update_driver_profile(user_id: int, request):
    """Update driver profile information"""

    user = user_repo.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user_repo.is_driver(user_id):
        raise HTTPException(status_code=403, detail="User is not a driver")

    if(
        request.name is None
        and request.vehicle_type is None
        and request.is_available is None
    ):
        raise HTTPException(status_code=400, detail="No fields provided")

    driver = user_repo.get_driver_by_user_id(user_id)

    if request.name is not None:
        user["name"] = request.name

    if request.vehicle_type is not None:
        driver["vehicle_type"] = request.vehicle_type

    if request.is_available is not None:
        driver["is_available"] = request.is_available

    return{
        "user_id": user_id,
        "name": user["name"],
        "vehicle_type": driver["vehicle_type"],
        "is_available": driver["is_available"],
        "message": "Driver profile updated successfully",
    }
