"""Router for restaurant endpoints"""

from typing import Any, Optional, Dict

from fastapi import APIRouter, Header, Request, status

from backend.app.schemas.restaurant import (
    RestaurantOut, RestaurantCreate, RestaurantUpdate,
    MenuItemCreate, MenuItemUpdate,
)
from backend.app.schemas.menu import MenuItemOut
from backend.app.services.restaurants_service import (
    get_restaurant_menu,
    get_all_restaurants_list,
    create_new_restaurant,
    update_restaurant_by_id,
    delete_restaurant_by_id,
    add_menu_item,
    update_menu_item_by_id,
    delete_menu_item_by_id,
    search_restaurant,
    search_menu_items,
)
from backend.app.services.role_service import require_manager
from backend.app.data.categories_data import VALID_CATEGORIES, VALID_DIETARY_TAGS

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

def get_session_token(
        request: Request,
        session_token: Optional[str] = Header(default=None),
) -> Optional[str]:
    """Return session token from header or cookie"""
    if session_token:
        return session_token

    return request.cookies.get("session_token")

def authenticate_manager(
        request: Request,
        session_token: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    """Authenticate the user and ensure they are a manager"""
    token = get_session_token(request, session_token)
    return require_manager(token)

@router.get("", response_model=list[RestaurantOut])
def read_all_restaurants():
    """Endpoint to get a list of all restaurants"""
    return get_all_restaurants_list()

@router.get("/{restaurant_id}/menu", response_model=RestaurantOut)
def read_restaurant_menu(restaurant_id: int):
    """Endpoint to get a restaurant menu with price formatting and status"""
    return get_restaurant_menu(restaurant_id)

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(restaurant_id: int,
                      request: Request,
                      session_token: Optional[str] = Header(default=None),):
    """Endpoint to delete a restaurant if it has no active menu items"""
    authenticate_manager(request, session_token)
    delete_restaurant_by_id(restaurant_id)

@router.delete("/{restaurant_id}/menu/{item_id}",
               status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(restaurant_id: int,
                     item_id: int,
                     request: Request,
                     session_token: Optional[str] = Header(default=None),):
    """Endpoint to delete a menu item by id"""
    authenticate_manager(request, session_token)
    delete_menu_item_by_id(restaurant_id, item_id)

@router.post("", response_model=RestaurantOut, status_code=status.HTTP_201_CREATED)
def create_restaurant(body: RestaurantCreate,
                      request: Request,
                      session_token: Optional[str] = Header(default=None),):
    """Endpoint to create a new restaurant"""
    token = get_session_token(request, session_token)
    session = require_manager(token)
    return create_new_restaurant(body, owner_id=session["user_id"])

@router.post("/{restaurant_id}/menu",
             response_model=MenuItemOut,
             status_code=status.HTTP_201_CREATED)
def create_menu_item(restaurant_id: int,
                     item: MenuItemCreate,
                     request: Request,
                     session_token: Optional[str] = Header(default=None),):
    """Endpoint to add a new menu item to a restaurant"""
    authenticate_manager(request, session_token)
    return add_menu_item(restaurant_id, item)

@router.patch("/{restaurant_id}", response_model=RestaurantOut)
def patch_restaurant(
    restaurant_id: int,
    body: RestaurantUpdate,
    request: Request,
    session_token: Optional[str] = Header(default=None),
):
    """Endpoint to update restaurant details"""
    authenticate_manager(request, session_token)
    return update_restaurant_by_id(restaurant_id, body)

@router.patch("/{restaurant_id}/menu/{item_id}", response_model=MenuItemOut)
def patch_menu_item(
    restaurant_id: int,
    item_id: int,
    body: MenuItemUpdate,
    request: Request,
    session_token: Optional[str] = Header(default=None),
):
    """Endpoint to update a menu item"""
    authenticate_manager(request, session_token)
    return update_menu_item_by_id(restaurant_id, item_id, body)

@router.get("/categories")
def list_categories():
    """Test endpoint to list valid categories and dietary tags for menu items"""
    return {
        "categories": [{"id": k, "name": v} for k, v in VALID_CATEGORIES.items()],
        "dietary_tags": list(VALID_DIETARY_TAGS),
    }

@router.get("/search")
def search_restaurants_endpoint(q: str):
    """Endpoint to search restaurants by name"""
    return search_restaurant(q)

@router.get("/menu/search")
def search_menu_items_endpoint(q: str):
    """Endpoint to search menu items by name"""
    return search_menu_items(q)
