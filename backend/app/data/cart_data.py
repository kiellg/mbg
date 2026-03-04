"""This module simulates a database of restaurant records"""

from typing import Dict, Any

_CARTDB: Dict[int, Dict[str, Any]] = {}

_NEXT_CART_ID: int = 1
_NEXT_ITEM_ID: int = 1
