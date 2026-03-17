"""Repository functions for restaurant data management"""
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

import copy
from typing import Dict, Any, List, Optional
from backend.app.data.restaurants_data import _DB, _SEED
from backend.app.pagination import paginate

def get_restaurant_record(restaurant_id: int) -> Optional[Dict[str, Any]]:
    """Simulate fetching a restaurant record from the database"""
    return _DB.get(restaurant_id)

def get_all_restaurants() -> List[Dict[str, Any]]:
    """Simulate fetching all restaurant records from the database"""
    return list(_DB.values())

def create_restaurant(
    name: str,
    address: str,
    rating: Optional[int],
    opening_hours: str,
    owner_id: str,
    cuisine_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Create and store a new restaurant record"""
    new_id = max(_DB.keys(), default=0) + 1
    restaurant = {
        "id": new_id,
        "name": name,
        "address": address,
        "rating": rating,
        "opening_hours": opening_hours,
        "owner_id": owner_id,
        "cuisine_type": cuisine_type,
        "menu": [],
    }
    _DB[new_id] = restaurant
    return restaurant


def update_restaurant(
    restaurant_id: int,
    patch: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Update fields on an existing restaurant record"""
    restaurant = _DB.get(restaurant_id)
    if not restaurant:
        return None
    for field in ("name", "address", "rating", "opening_hours"):
        if field in patch and patch[field] is not None:
            restaurant[field] = patch[field]
    return restaurant

def delete_restaurant(restaurant_id: int) -> bool:
    """Remove a restaurant from the simulated DB"""
    if restaurant_id not in _DB:
        return False
    del _DB[restaurant_id]
    return True

def get_menu_item(restaurant_id: int, menu_item_id: int) -> Optional[Dict[str, Any]]:
    """Return a single menu item by restaurant and item ID."""
    restaurant = _DB.get(restaurant_id)
    if not restaurant:
        return None
    for item in restaurant["menu"]:
        if item["id"] == menu_item_id:
            return item
    return None

def add_menu_item(
    restaurant_id: int,
    item_data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Add a new menu item to a restaurant"""
    restaurant = _DB.get(restaurant_id)
    if not restaurant:
        return None
    existing_ids = [i["id"] for i in restaurant["menu"]]
    new_id = max(existing_ids, default=0) + 1
    new_item = {
        "id": new_id,
        "restaurant_id": restaurant_id,
        "name": item_data["name"],
        "price_cents": item_data["price_cents"],
        "description": item_data.get("description", ""),
        "dietary_tag": item_data.get("dietary_tag", ""),
        "is_visible": item_data.get("is_visible", True),
        "is_active": item_data.get("is_active", True),
        "is_available": item_data.get("is_available", True),
        "category": {
            "id": item_data.get("category_id"),
            "name": "",
        },
    }
    restaurant["menu"].append(new_item)
    return new_item


def update_menu_item(
    restaurant_id: int,
    item_id: int,
    patch: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Update fields on an existing menu item"""
    restaurant = _DB.get(restaurant_id)
    if not restaurant:
        return None
    for item in restaurant["menu"]:
        if item["id"] == item_id:
            for field in ("name", "description", "dietary_tag",
                          "price_cents", "is_visible", "is_active",
                          "is_available", "category_id"):
                if field in patch and patch[field] is not None:
                    item[field] = patch[field]
            return item
    return None

def delete_menu_item(restaurant_id: int, item_id: int) -> bool:
    """Remove a menu item from a restaurant"""
    restaurant = _DB.get(restaurant_id)
    if not restaurant:
        return False
    original_len = len(restaurant["menu"])
    restaurant["menu"] = [i for i in restaurant["menu"] if i["id"] != item_id]
    return len(restaurant["menu"]) < original_len

def get_active_menu_items(restaurant_id: int) -> List[Dict[str, Any]]:
    """Return all active menu items for a restaurant"""
    restaurant = _DB.get(restaurant_id)
    if not restaurant:
        return []
    return [i for i in restaurant["menu"] if i.get("is_active", True)]

def reset_restaurants() -> None:
    """Reset the simulated restaurant DB for testing only"""
    _DB.clear()
    _DB.update(copy.deepcopy(_SEED))

def search_restaurant_by_name(query: str) -> List[Dict[str, Any]]:
    """Return restaurants whose names partially match the search query"""
    query_lower = query.lower()
    results = []

    for restaurant in _DB.values():
        if query_lower in restaurant["name"].lower():
            results.append(restaurant)

    return results

def search_menu_items_by_name(query: str) -> List[Dict[str, Any]]:
    """Return menu items whose names partially match the search query"""
    query_lower = query.lower()
    results = []

    for restaurant in _DB.values():
        for item in restaurant.get("menu", []):
            if query_lower in item["name"].lower():
                results.append({
                    "id": item["id"],
                    "name": item["name"],
                    "restaurant_id": restaurant["id"],
                    "restaurant_name": restaurant["name"],
                })

    return results

def filter_restaurants_by_cuisine(
        cuisine_types: list[str] | None,
) -> List[Dict[str, Any]]:
    """Return restaurants that match cuisine filters"""
    if not cuisine_types:
        return list(_DB.values())

    results = []

    for restaurant in _DB.values():
        cuisine = restaurant.get("cuisine_type")

        if cuisine in cuisine_types:
            results.append(restaurant)

    return results

def filter_menu_items(
        restaurant_id: int,
        categories: list[int] | None,
        dietary_tags: list[str] | None,
        min_price: int | None,
        max_price: int | None,
) -> List[Dict[str, Any]]:
    """Return menu items that match filter conditions"""
    restaurant = _DB.get(restaurant_id)

    if not restaurant:
        return []

    results = []

    for item in restaurant.get("menu", []):
        if categories:
            cat = item.get("category") or {}
            if cat.get("id") not in categories:
                continue

        if dietary_tags:
            if item.get("dietary_tag") not in dietary_tags:
                continue

        cents = item.get("price_cents")

        if min_price is not None and cents is not None:
            if cents < min_price:
                continue

        if max_price is not None and cents is not None:
            if cents > max_price:
                continue

        results.append(item)

    return results

def get_restaurants_paginated(page: int, limit: int):
    """Returned paginated restaurants records"""
    restaurants = list(_DB.values())
    total = len(restaurants)

    items = paginate(restaurants, page, limit)

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
    }

def get_menu_items_paginated(restaurant_id: int, page: int, limit: int):
    """Return paginated menu items for a restaurant"""
    restaurant = _DB.get(restaurant_id)

    if not restaurant:
        raise ValueError("Restaurant not found")

    menu = restaurant.get("menu", [])
    total = len(menu)

    items = paginate(menu, page, limit)

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
    }

def sort_restaurants(
        restaurants: list[Dict[str, Any]],
        sort_by: str,
        order: str,
) -> list[Dict[str, Any]]:
    """Sort restaurants by supported fields"""
    reverse = order == "desc"

    if sort_by == "rating":
        return sorted(restaurants, key=lambda r: r.get("rating", 0), reverse=reverse)

    return restaurants

def sort_menu_items(
        menu_items: list[Dict[str, Any]],
        sort_by: str,
        order: str,
) -> list[Dict[str, Any]]:
    """Sort menu items by supported fields"""
    reverse = order == "desc"

    if sort_by == "price":
        return sorted(menu_items, key=lambda m: m.get("price_cents", 0), reverse=reverse)

    return menu_items
