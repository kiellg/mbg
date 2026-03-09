"""Router for restaurant endpoints"""

from fastapi import APIRouter, Header, status

from backend.app.schemas.restaurant import RestaurantOut, MenuItemCreate
from backend.app.schemas.menu import MenuItemOut
from backend.app.services.restaurants_service import (
    get_restaurant_menu,
    delete_restaurant_by_id,
    delete_menu_item_by_id,
    add_menu_item
)
from backend.app.services.role_service import require_manager, require_role

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("/{restaurant_id}/menu", response_model=RestaurantOut)
def read_restaurant_menu(restaurant_id: int, session_token: str = Header(...)):
    """Endpoint to get a restaurant menu with price formatting and status"""
    require_role(session_token, ["customer", "manager", "driver"])
    return get_restaurant_menu(restaurant_id)

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(restaurant_id: int, session_token: str = Header(...)):
    """Endpoint to delete a restaurant if it has no active menu items"""
    require_manager(session_token)
    delete_restaurant_by_id(restaurant_id)

@router.delete("/{restaurant_id}/menu/{item_id}",
               status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(restaurant_id: int, item_id: int, session_token: str = Header(...)):
    """Endpoint to delete a menu item by id"""
    require_manager(session_token)
    delete_menu_item_by_id(restaurant_id, item_id)

@router.post("/{restaurant_id}/menu",
             response_model=MenuItemOut,
             status_code=status.HTTP_201_CREATED)
def create_menu_item(restaurant_id: int, item: MenuItemCreate, session_token: str = Header(...)):
    """Endpoint to add a new menu item to a restaurant"""
    require_manager(session_token)
    return add_menu_item(restaurant_id, item)
