"""Service layer for restaurant-related business logic"""

import copy

from fastapi import HTTPException

from backend.app.data.categories_data import VALID_CATEGORIES
from backend.app.schemas.restaurant import (
    RestaurantOut, RestaurantCreate, RestaurantUpdate,
    MenuItemCreate, MenuItemUpdate, RestaurantSearchResult,
    MenuItemSearchResult,
)
from backend.app.schemas.menu import PriceStatus
from backend.app.repositories.restaurant_repo import (
    get_restaurant_record,
    get_all_restaurants,
    get_active_menu_items,
    create_restaurant,
    update_restaurant as repo_update_restaurant,
    delete_restaurant,
    add_menu_item as repo_add_menu_item,
    update_menu_item as repo_update_menu_item,
    delete_menu_item,
    search_restaurant_by_name,
    search_menu_items_by_name,
    filter_restaurants_by_cuisine,
    filter_menu_items,
)
from backend.app.utils.formatting import format_cad_from_cents

def get_all_restaurants_list() -> list[RestaurantOut]:
    """Fetch all restaurants"""
    return get_all_restaurants()

def get_restaurant_menu(restaurant_id: int) -> RestaurantOut:
    """Fetch restaurant data and process menu items for display"""
    record = get_restaurant_record(restaurant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    record = copy.deepcopy(record)

    for item in record.get("menu", []):
        item["restaurant_id"] = restaurant_id

        cat = item.get("category") or {}
        cat_id = cat.get("id") if isinstance(cat, dict) else None
        if cat_id and cat_id in VALID_CATEGORIES:
            item["category"] = {"id": cat_id, "name": VALID_CATEGORIES[cat_id]}

        visible = item.get("is_visible", True)
        active = item.get("is_active", True)
        cents = item.get("price_cents", None)

        if not (visible and active):
            item["display_price"] = None
            item["price_status"] = PriceStatus.OK
            continue

        if cents is None:
            item["display_price"] = None
            item["price_status"] = PriceStatus.MISSING
        elif cents < 0:
            item["display_price"] = None
            item["price_status"] = PriceStatus.INVALID
        else:
            item["display_price"] = format_cad_from_cents(cents)
            item["price_status"] = PriceStatus.OK

    return RestaurantOut(**record)

def delete_restaurant_by_id(restaurant_id: int) -> None:
    """Delete a restaurant only if it has no active menu items"""
    record = get_restaurant_record(restaurant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    active_items = get_active_menu_items(restaurant_id)
    if active_items:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete restaurant with active menu items. "
                   "Please remove or deactivate all menu items first.",
        )
    delete_restaurant(restaurant_id)

def delete_menu_item_by_id(restaurant_id: int, item_id: int) -> None:
    """Delete a menu item from a restaurant"""
    record = get_restaurant_record(restaurant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    removed = delete_menu_item(restaurant_id, item_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Menu item not found")

def create_new_restaurant(item: RestaurantCreate, owner_id: str) -> dict:
    """Create a new restaurant record"""
    args = {
        "name": item.name,
        "address": item.address,
        "rating": item.rating,
        "opening_hours": item.opening_hours,
        "owner_id": owner_id,
    }

    if item.cuisine_type is not None:
        args["cuisine_type"] = item.cuisine_type

    return create_restaurant(**args)

def add_menu_item(restaurant_id: int, item: MenuItemCreate) -> dict:
    """Add a new menu item to a restaurant"""
    record = get_restaurant_record(restaurant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return repo_add_menu_item(restaurant_id, item.model_dump())

def update_restaurant_by_id(restaurant_id: int, patch: RestaurantUpdate) -> dict:
    """Update restaurant fields"""
    record = get_restaurant_record(restaurant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return repo_update_restaurant(restaurant_id, patch.model_dump(exclude_none=True))

def update_menu_item_by_id(restaurant_id: int, item_id: int, patch: MenuItemUpdate) -> dict:
    """Update menu item fields"""
    record = get_restaurant_record(restaurant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    updated = repo_update_menu_item(restaurant_id, item_id, patch.model_dump(exclude_none=True))
    if updated is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return updated

def search_restaurant(query: str) -> list[RestaurantSearchResult]:
    """Search restaurant by name"""
    results = search_restaurant_by_name(query)
    return [
        RestaurantSearchResult(
            id=r["id"],
            name=r["name"],
            address=r["address"],
            rating=r["rating"],
        )
        for r in results
    ]

def search_menu_items(query: str) -> list[MenuItemSearchResult]:
    """Search menu items by name"""
    results = search_menu_items_by_name(query)
    return [
        MenuItemSearchResult(**item)
        for item in results
    ]

def filter_restaurants(cuisine_types: list[str] | None):
    """Filter restaurants by cuisine type"""
    return filter_restaurants_by_cuisine(cuisine_types)

def filter_menu_items_service(
        restaurant_id: int,
        categories: list[int] | None,
        dietary_tags: list[str] | None,
        min_price: int | None,
        max_price: int | None,
):
    """Filter menu items by category, dietary tags, and price"""
    record = get_restaurant_record(restaurant_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return filter_menu_items(
        restaurant_id,
        categories,
        dietary_tags,
        min_price,
        max_price,
    )
