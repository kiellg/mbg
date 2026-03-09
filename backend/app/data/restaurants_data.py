"""This module simulates a database of restaurant records"""

from typing import Dict, Any
import copy

_SEED: Dict[int, Dict[str, Any]] = {
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

_DB: Dict[int, Dict[str, Any]] = copy.deepcopy(_SEED)
