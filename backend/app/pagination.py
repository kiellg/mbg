"""Helper function for paginating lists"""

from typing import Any, List

def paginate(items: List[Any], page: int, limit: int) -> List[Any]:
    """Return a slice of items for the requested page"""
    start = (page - 1) * limit
    end = start + limit
    return items[start:end]
