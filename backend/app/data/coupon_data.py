"""Seeded in-memory discount code data for checkout."""

import copy
from typing import Any, Dict, Optional

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


def get_coupon_record(code: str) -> Optional[Dict[str, Any]]:
    """Return the stored coupon record for a normalized code."""
    return _COUPONDB.get(code)


def list_coupon_records() -> Dict[str, Dict[str, Any]]:
    """Return the raw coupon store for internal read-only access."""
    return _COUPONDB


def set_coupon_record(code: str, record: Dict[str, Any]) -> None:
    """Store a coupon record for tests or internal setup."""
    _COUPONDB[code] = record


def reset_coupon_store() -> None:
    """Reset the coupon store back to the seeded records."""
    _COUPONDB.clear()
    _COUPONDB.update(copy.deepcopy(_SEED))
