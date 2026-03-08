"""This module simulates a database of order records."""

from typing import Any, Dict, List, Optional

_ORDERDB: Dict[int, Dict[str, Any]] = {}

NEXT_ORDER_ID: int = 1
NEXT_ORDER_ITEM_ID: int = 1