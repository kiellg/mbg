"""Repository for recently viewed items"""

from typing import List, Dict, Any
from backend.app.data.recently_viewed_data import _RECENTLY_VIEWED

MAX_ITEMS = 10

def get_recently_viewed(user_id: str) -> List[Dict[str, Any]]:
    """Return recently viewed items for a user"""
    return _RECENTLY_VIEWED.get(user_id, [])

def add_recently_viewed(user_id: str, item: Dict[str, Any]) -> None:
    """Add an item to recently viewed list"""
    items = _RECENTLY_VIEWED.setdefault(user_id, [])

    items = [
        i for i in items
        if not (i["type"] == item["type"] and i["id"] == item["id"])
    ]

    items.insert(0, item)

    _RECENTLY_VIEWED[user_id] = items[:MAX_ITEMS]
