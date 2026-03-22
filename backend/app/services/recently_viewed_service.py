"""Service layer for recently viewed items"""

import time
from backend.app.repositories.recently_viewed_repo import(
    get_recently_viewed,
    add_recently_viewed,
)

def track_recently_viewed(user_id: str, item_type: str, item_id: int) -> None:
    """Track a viewed item"""
    item = {
        "type": item_type,
        "id": item_id,
        "timestamp": int(time.time()),
    }

    add_recently_viewed(user_id, item)

def get_recent_items(user_id: str):
    """Get recently viewed items"""
    return get_recently_viewed(user_id)
