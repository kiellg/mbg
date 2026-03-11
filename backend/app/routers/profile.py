"""Router endpoints for profile management"""

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_current_user
from backend.app.schemas.profile import(
    CustomerProfileUpdateRequest,
    CustomerProfileUpdateResponse,
    RestaurantProfileUpdateRequest,
    RestaurantProfileUpdateResponse,
)
from backend.app.services import profile_service

router = APIRouter(prefix="/profile", tags=["profile"])

@router.patch("/customer", response_model=CustomerProfileUpdateResponse)
def update_customer_profile(
    request: CustomerProfileUpdateRequest,
    current_user = Depends(get_current_user),
):
    """Update the logged in customer's profile"""
    result = profile_service.update_customer_profile(
        user_id=current_user["user_id"],
        name=request.name,
        delivery_address=request.delivery_address,
    )

    return result

@router.patch("/restaurant/{restaurant_id}",
              response_model=RestaurantProfileUpdateResponse
)
def update_restaurant_profile(
    restaurant_id: int,
    request: RestaurantProfileUpdateRequest,
    current_user=Depends(get_current_user),
):
    """Manager updates restaurant profile"""

    return profile_service.update_manager_restaurant_profile(
        user_id=current_user["user_id"],
        restaurant_id=restaurant_id,
        request=request,
    )
