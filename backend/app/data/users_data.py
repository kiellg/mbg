"""Raw in-memory user data"""

from typing import Dict, Any

USERS: Dict[str, Dict[str, Any]] = {}
CUSTOMERS: Dict[int, Dict[str, Any]] = {}
MANAGERS: Dict[int, Dict[str, Any]] = {}
DRIVERS: Dict[int, Dict[str, Any]] = {}

NEXT_USER_ID = 1
