"""Raw in-memory user data"""

from typing import Dict, Any

USERS: Dict[str, Dict[str, Any]] = {}
CUSTOMERS: Dict[str, Dict[str, Any]] = {}
MANAGERS: Dict[str, Dict[str, Any]] = {}
DRIVERS: Dict[str, Dict[str, Any]] = {}

PASSWORD_RESET_TOKENS: Dict[str, Dict[str, Any]] = {}
