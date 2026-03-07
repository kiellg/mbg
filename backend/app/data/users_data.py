"""Raw in-memory user data"""

from typing import Dict, Any

_USERS: Dict[str, Dict[str, Any]] = {}
_CUSTOMERS: Dict[int, Dict[str, Any]] = {}
_MANAGERS: Dict[int, Dict[str, Any]] = {}
_DRIVERS: Dict[int, Dict[str, Any]] = {}

_NEXT_USER_ID = 1
