"""Simulated in-memory database for payment records"""

from typing import Any, Dict

_PAYMENTDB: Dict[str, Dict[str, Any]] = {}
_TOKENDB: Dict[str, str] = {}
