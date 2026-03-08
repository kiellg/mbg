"""This module simulates a database of restaurant records"""

from typing import Dict, Any, List, Optional

_DB: Dict[int, Dict[str, Any]] = {
    1: {
        "id": 1,
        "name": "The Keg Steakhouse",
        "address": "67 Bernard Ave, Kelowna, BC",
        "rating": 4,
        "opening_hours": "Mon-Sun 11:30-22:00",
        "menu": [
            {
                "id": 1,
                "name": "Ribeye Steak",
                "price_cents": 4999,
                "description": "12oz AAA ribeye with garlic mashed potatoes",
                "dietary_tag": "",
                "is_visible": True,
                "is_active": True,
                "is_available": True,
                "category": {"id": 10, "name": "Mains"},
            },
            {
                "id": 2,
                "name": "Lobster Tail",
                "price_cents": 999,
                "description": "Market price item, check with server",
                "dietary_tag": "",
                "is_visible": False,
                "is_active": True,
                "is_available": True,
                "category": {"id": 10, "name": "Mains"},
            },
            {
                "id": 3,
                "name": "House Red Wine",
                "price_cents": -200,
                "description": "Glass of BC VQA red wine",
                "dietary_tag": "vegan",
                "is_visible": True,
                "is_active": True,
                "is_available": True,
                "category": {"id": 20, "name": "Drinks"},
            },
            {
                "id": 4,
                "name": "Seasonal Soup",
                "price_cents": None,
                "description": "Ask your server for today's soup",
                "dietary_tag": "vegetarian",
                "is_visible": True,
                "is_active": True,
                "is_available": True,
                "category": {"id": 30, "name": "Starters"},
            },
        ],
    },
    2: {
        "id": 2,
        "name": "Sushi World",
        "address": "123 Sushi St, Vancouver, BC",
        "rating": 5,
        "opening_hours": "Mon-Sun 12:00-23:00",
        "menu": [
            {
                "id": 1,
                "name": "California Roll",
                "price_cents": 899,
                "description": "Crab, avocado, cucumber, and mayo",
                "dietary_tag": "",
                "is_visible": True,
                "is_active": True,
                "is_available": True,
                "category": {"id": 10, "name": "Mains"},
            },
            {
                "id": 2,
                "name": "Spicy Tuna Roll",
                "price_cents": 999,
                "description": "Tuna mixed with spicy mayo",
                "dietary_tag": "",
                "is_visible": True,
                "is_active": True,
                "is_available": True,
                "category": {"id": 10, "name": "Mains"},
            },
        ],
    },
}

def get_restaurant_record(restaurant_id: int) -> Optional[Dict[str, Any]]:
    """Simulate fetching a restaurant record from the database"""
    return _DB.get(restaurant_id)

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

def delete_restaurant(restaurant_id: int) -> bool:
    """Remove a restaurant from the simulated DB"""
    if restaurant_id not in _DB:
        return False
    del _DB[restaurant_id]
    return True
