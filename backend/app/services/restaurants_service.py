"""Service layer for restaurant-related business logic"""

from fastapi import HTTPException

from backend.app.schemas.restaurant import RestaurantOut, MenuItemCreate
from backend.app.schemas.menu import PriceStatus
from backend.app.repositories.restaurant_repo import (
    get_restaurant_record,
    delete_restaurant,
    delete_menu_item,
    get_active_menu_items
)

def format_cad_from_cents(price_cents: int) -> str:
    """Convert price in cents to a formatted CAD string"""
    return f"${price_cents / 100:.2f}"

def get_restaurant_menu(restaurant_id: int) -> RestaurantOut:
    """Fetch restaurant data and process menu items for display"""
    record = get_restaurant_record(restaurant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    for item in record.get("menu", []):
        item["restaurant_id"] = restaurant_id

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
    """Delete a restaurant only if it has no active menu items (US21)"""
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

def add_menu_item(restaurant_id: int, item: MenuItemCreate) -> dict:
    """Add a new menu item to a restaurant"""
    record = get_restaurant_record(restaurant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    existing_ids = [i["id"] for i in record["menu"]]
    new_id = max(existing_ids, default=0) + 1

    new_item = {
        "id": new_id,
        "restaurant_id": restaurant_id,
        "name": item.name,
        "price_cents": item.price_cents,
        "description": item.description,
        "dietary_tag": item.dietary_tag,
        "is_visible": item.is_visible,
        "is_active": item.is_active,
        "is_available": item.is_available,
        "category": {"id": item.category_id, "name": ""},
    }
    record["menu"].append(new_item)
    return new_item
