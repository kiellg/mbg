"""Simulated in-memory database for payment records"""

from typing import Any, Dict

_PAYMENTDB: Dict[str, Dict[str, Any]] = {}