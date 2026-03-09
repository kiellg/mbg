"""Repository functions for restaurant data management"""

from typing import Dict, Any, List, Optional
from backend.app.data.restaurants_data import _DB

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
    owner_id: int,
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
        **item_data,
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
    _DB.update({
        1: {
            "id": 1,
            "name": "The Keg Steakhouse",
            "address": "67 Bernard Ave, Kelowna, BC",
            "rating": 4,
            "opening_hours": "Mon-Sun 11:30-22:00",
            "owner_id": 1,
            "menu": [
                {
                    "id": 1,
                    "restaurant_id": 1,
                    "name": "Ribeye Steak",
                    "price_cents": 4999,
                    "description": "12oz AAA ribeye with garlic mashed potatoes",
                    "dietary_tag": "",
                    "is_visible": True,
                    "is_active": True,
                    "is_available": True,
                    "category": {"id": 10, "name": "Mains"},
                },
            ],
        },
        2: {
            "id": 2,
            "name": "Sushi World",
            "address": "123 Sushi St, Vancouver, BC",
            "rating": 5,
            "opening_hours": "Mon-Sun 12:00-23:00",
            "owner_id": 2,
            "menu": [
                {
                    "id": 1,
                    "restaurant_id": 2,
                    "name": "California Roll",
                    "price_cents": 899,
                    "description": "Crab, avocado, cucumber, and mayo",
                    "dietary_tag": "",
                    "is_visible": True,
                    "is_active": True,
                    "is_available": True,
                    "category": {"id": 10, "name": "Mains"},
                },
            ],
        },
    })
