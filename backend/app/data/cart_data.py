"""This module simulates a database of restaurant records"""

from typing import Dict, Any, Optional

_CartDB: Dict[int, Dict[str, Any]] = {}

next_cart_id: int = 1
_next_item_id: int = 1
