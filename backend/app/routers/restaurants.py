"""Router for restaurant endpoints"""

from fastapi import APIRouter

from backend.app.schemas.restaurant import RestaurantOut
from backend.app.services.restaurants_service import get_restaurant_menu

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("/{restaurant_id}/menu", response_model=RestaurantOut)
def read_restaurant_menu(restaurant_id: int):
    """Endpoint to get a restaurant menu with price formatting and status"""
    return get_restaurant_menu(restaurant_id)
