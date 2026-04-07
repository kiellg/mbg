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


def reset_coupons() -> None:
    """Reset the coupon store back to the seeded records."""
    COUPON_DB.clear()
    COUPON_DB.update(copy.deepcopy(COUPON_SEED))


def put_coupon_record(code: str, record: Dict[str, Any]) -> None:
    """Store a coupon record for testing or internal setup."""
    COUPON_DB[code] = copy.deepcopy(record)
