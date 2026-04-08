"""Raw in-memory user data"""

import copy
import hashlib
from typing import Dict, Any

SEEDED_ADMIN_USER_ID = "00000000-0000-0000-0000-000000000001"
SEEDED_ADMIN_EMAIL = "admin@chow.com"
SEEDED_ADMIN_PASSWORD = "admin123"

USER_SEED: Dict[str, Dict[str, Any]] = {
    SEEDED_ADMIN_EMAIL: {
        "user_id": SEEDED_ADMIN_USER_ID,
        "name": "Admin",
        "email": SEEDED_ADMIN_EMAIL,
        "password_hash": hashlib.sha256(SEEDED_ADMIN_PASSWORD.encode()).hexdigest(),
    }
}
ADMIN_SEED: Dict[str, Dict[str, Any]] = {
    SEEDED_ADMIN_USER_ID: {
        "user_id": SEEDED_ADMIN_USER_ID,
        "admin_id": SEEDED_ADMIN_USER_ID,
    }
}

USERS: Dict[str, Dict[str, Any]] = copy.deepcopy(USER_SEED)
CUSTOMERS: Dict[str, Dict[str, Any]] = {}
MANAGERS: Dict[str, Dict[str, Any]] = {}
DRIVERS: Dict[str, Dict[str, Any]] = {}
ADMINS: Dict[str, Dict[str, Any]] = copy.deepcopy(ADMIN_SEED)

PASSWORD_RESET_TOKENS: Dict[str, Dict[str, Any]] = {}
