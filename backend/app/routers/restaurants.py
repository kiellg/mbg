"""Router for restaurant endpoints"""

from typing import Any, Optional, Dict

from fastapi import APIRouter, Header, Request, status, Query

from backend.app.schemas.restaurant import (
    RestaurantOut, RestaurantCreate, RestaurantUpdate,
    MenuItemCreate, MenuItemUpdate,
)
from backend.app.schemas.menu import MenuItemOut
from backend.app.services.restaurants_service import (
    get_restaurant_menu,
    get_all_restaurants_list,
    get_all_restaurants_paginated,
    get_restaurant_menu_paginated,
    create_new_restaurant,
    update_restaurant_by_id,
    delete_restaurant_by_id,
    add_menu_item,
    update_menu_item_by_id,
    delete_menu_item_by_id,
    search_restaurant,
    search_menu_items,
    filter_restaurants,
    get_menu_item_detail,
    get_search_suggestions,
)
from backend.app.services.role_service import require_manager
from backend.app.data.categories_data import VALID_CATEGORIES, VALID_DIETARY_TAGS
from backend.app.schemas.search import SuggestionResponse
from backend.app.services.recently_viewed_service import track_recently_viewed
from backend.app.repositories.session_repo import get_session

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
    """Return all restaurants"""
    return get_all_restaurants_list()

@router.get("/{restaurant_id}/menu", response_model=RestaurantOut)
def read_restaurant_menu(
    restaurant_id: int,
    request: Request = None,
    session_token: Optional[str] = Header(default=None),
):
    """Endpoint to get a restaurant menu with price formatting and status (supports pagination)"""
    result = get_restaurant_menu(restaurant_id)

    if request:
        try:
            token = get_session_token(request, session_token)
            session = get_session(token)

            if session:
                track_recently_viewed(session["user_id"], "restaurant", restaurant_id)
        except (KeyError, TypeError):
            pass
    return result

@router.get("/paginated")
def read_all_restaurants_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
):
    """Return paginated restaurants"""
    return get_all_restaurants_paginated(page, limit)

@router.get("/{restaurant_id}/menu/paginated")
def read_restaurant_menu_paginated(
    restaurant_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
):
    """Return paginated restaurant menu"""
    return get_restaurant_menu_paginated(restaurant_id, page, limit)

@router.get("/sorted", response_model=list[RestaurantOut])
def read_all_restaurants_sorted(
    sort_by: str = Query("rating"),
    order: str = Query("desc"),
):
    """Return all restaurants sorted by given criteria"""
    return get_all_restaurants_list(sort_by, order)

@router.get("/paginated/sorted")
def read_all_restaurants_paginated_sorted(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    sort_by: str = Query("rating"),
    order: str = Query("desc"),
):
    """Return paginated restaurants with sorting"""
    return get_all_restaurants_paginated(page, limit, sort_by, order)

@router.get("/{restaurant_id}/menu/paginated/sorted")
def read_restaurant_menu_paginated_sorted(
    restaurant_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
):
    """Return sorted paginated menu items"""
    return get_restaurant_menu_paginated(
        restaurant_id,
        page,
        limit,
        sort_by,
        order,
    )

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

@router.get("/search/suggestions", response_model=SuggestionResponse)
def search_suggestions_endpoint(q: str):
    """Return search suggestions as user types"""
    return get_search_suggestions(q)

@router.get("/filter")
def filter_restaurants_endpoint(cuisine_types: Optional[list[str]] = Query(None)):
    """Endpoint to filter restaurants by cuisine type"""
    return filter_restaurants(cuisine_types)

@router.get("/{restaurant_id}/menu/{item_id}", response_model=MenuItemOut)
def read_menu_item_detail(
    restaurant_id: int,
    item_id: int,
    request: Request = None,
    session_token: Optional[str] = Header(default=None),
):
    """Return detailed information for a single menu item"""
    result = get_menu_item_detail(restaurant_id, item_id)

    if request:
        try:
            token = get_session_token(request, session_token)
            session = get_session(token)

            if session:
                track_recently_viewed(session["user_id"], "menu_item", item_id)

        except (KeyError, TypeError):
            pass

    return result
