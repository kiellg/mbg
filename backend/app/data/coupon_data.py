"""Seeded in-memory discount code data for checkout."""

from typing import Any, Dict
import copy

_SEED: Dict[str, Dict[str, Any]] = {
    "SAVE10": {
        "code": "SAVE10",
        "discount_type": "percentage",
        "percent_off": 10,
        "amount_off_cents": None,
        "minimum_subtotal_cents": 0,
        "expires_at": "2099-12-31T23:59:59+00:00",
        "is_active": True,
    },
    "TAKE7": {
        "code": "TAKE7",
        "discount_type": "fixed_amount",
        "percent_off": None,
        "amount_off_cents": 700,
        "minimum_subtotal_cents": 2000,
        "expires_at": "2099-12-31T23:59:59+00:00",
        "is_active": True,
    },
    "INACTIVE10": {
        "code": "INACTIVE10",
        "discount_type": "percentage",
        "percent_off": 10,
        "amount_off_cents": None,
        "minimum_subtotal_cents": 0,
        "expires_at": "2099-12-31T23:59:59+00:00",
        "is_active": False,
    },
    "EXPIRED5": {
        "code": "EXPIRED5",
        "discount_type": "fixed_amount",
        "percent_off": None,
        "amount_off_cents": 500,
        "minimum_subtotal_cents": 0,
        "expires_at": "2000-01-01T00:00:00+00:00",
        "is_active": True,
    },
    "MIN60": {
        "code": "MIN60",
        "discount_type": "percentage",
        "percent_off": 15,
        "amount_off_cents": None,
        "minimum_subtotal_cents": 6000,
        "expires_at": "2099-12-31T23:59:59+00:00",
        "is_active": True,
    },
}

_COUPONDB: Dict[str, Dict[str, Any]] = copy.deepcopy(_SEED)
