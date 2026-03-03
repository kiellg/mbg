"""
This module simulates a database of restaurant records. In a real application, this would be replaced by actual database queries.
"""

from typing import Dict, Any, Optional

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
    }
}

def get_restaurant_record(restaurant_id: int) -> Optional[Dict[str, Any]]:
    return _DB.get(restaurant_id)