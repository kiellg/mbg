"""This module simulates a database of order records."""

from typing import Any, Dict

_ORDERDB: Dict[str, Dict[str, Any]] = {}

NEXT_ORDER_ITEM_ID: int = 1
