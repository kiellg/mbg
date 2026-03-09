"""Router for restaurant endpoints"""

from typing import Optional

from fastapi import APIRouter, Header, Request, status

from backend.app.schemas.restaurant import RestaurantOut, MenuItemCreate
from backend.app.schemas.menu import MenuItemOut
from backend.app.services.restaurants_service import (
    get_restaurant_menu,
    delete_restaurant_by_id,
    delete_menu_item_by_id,
    add_menu_item
)
from backend.app.services.role_service import require_manager

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

def get_session_token(
        request: Request,
        session_token: Optional[str] = Header(default=None),
) -> Optional[str]:
    """Return session token from header or cookie"""
    if session_token:
        return session_token

    return request.cookies.get("session_token")

@router.get("/{restaurant_id}/menu", response_model=RestaurantOut)
def read_restaurant_menu(restaurant_id: int):
    """Endpoint to get a restaurant menu with price formatting and status"""
    return get_restaurant_menu(restaurant_id)

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(restaurant_id: int,
                      request: Request,
                      session_token: Optional[str] = Header(default=None),):
    """Endpoint to delete a restaurant if it has no active menu items"""
    token = get_session_token(request, session_token)
    require_manager(token)
    delete_restaurant_by_id(restaurant_id)

@router.delete("/{restaurant_id}/menu/{item_id}",
               status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(restaurant_id: int,
                     item_id: int,
                     request: Request,
                     session_token: Optional[str] = Header(default=None),):
    """Endpoint to delete a menu item by id"""
    token = get_session_token(request, session_token)
    require_manager(token)
    delete_menu_item_by_id(restaurant_id, item_id)

@router.post("/{restaurant_id}/menu",
             response_model=MenuItemOut,
             status_code=status.HTTP_201_CREATED)
def create_menu_item(restaurant_id: int,
                     item: MenuItemCreate,
                     request: Request,
                     session_token: Optional[str] = Header(default=None),):
    """Endpoint to add a new menu item to a restaurant"""
    token = get_session_token(request, session_token)
    require_manager(token)
    return add_menu_item(restaurant_id, item)
