"""This module simulates a database of restaurant records"""

from typing import Dict, Any, Optional

_CARTDB: Dict[int, Dict[str, Any]] = {}

NEXT_CART_ID: int = 1
NEXT_ITEM_ID: int = 1
