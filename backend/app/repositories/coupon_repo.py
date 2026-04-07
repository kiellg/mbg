"""Repository functions for seeded discount code records."""

import copy
from typing import Any, Dict, List, Optional

from app.data.coupon_data import COUPON_DB, COUPON_SEED


def get_coupon_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Return a coupon record by normalized code."""
    record = COUPON_DB.get(code)
    if record is None:
        return None
    return copy.deepcopy(record)


def list_coupons() -> List[Dict[str, Any]]:
    """Return all seeded coupon records."""
    return [
        copy.deepcopy(record)
        for _, record in sorted(COUPON_DB.items())
    ]


def create_coupon_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Create and store a coupon record."""
    COUPON_DB[record["code"]] = copy.deepcopy(record)
    return copy.deepcopy(COUPON_DB[record["code"]])


def update_coupon_record(code: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update a coupon record with known fields only."""
    record = COUPON_DB.get(code)
    if record is None:
        return None

    for field in (
        "discount_type",
        "percent_off",
        "amount_off_cents",
        "minimum_subtotal_cents",
        "expires_at",
        "is_active",
    ):
        if field in patch:
            record[field] = copy.deepcopy(patch[field])

    return copy.deepcopy(record)


def deactivate_coupon_record(code: str) -> Optional[Dict[str, Any]]:
    """Deactivate a coupon record."""
    return update_coupon_record(code, {"is_active": False})


def delete_coupon_record(code: str) -> bool:
    """Delete a coupon record by code."""
    if code not in COUPON_DB:
        return False

    del COUPON_DB[code]
    return True


def reset_coupons() -> None:
    """Reset the coupon store back to the seeded records."""
    COUPON_DB.clear()
    COUPON_DB.update(copy.deepcopy(COUPON_SEED))


def put_coupon_record(code: str, record: Dict[str, Any]) -> None:
    """Store a coupon record for testing or internal setup."""
    COUPON_DB[code] = copy.deepcopy(record)
