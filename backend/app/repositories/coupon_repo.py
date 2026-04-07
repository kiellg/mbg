"""Repository functions for seeded discount code records."""

import copy
from typing import Any, Dict, Optional

from app.data import coupon_data


def get_coupon_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Return a coupon record by normalized code."""
    record = coupon_data._COUPONDB.get(code)
    if record is None:
        return None
    return copy.deepcopy(record)


def reset_coupons() -> None:
    """Reset the coupon store back to the seeded records."""
    coupon_data._COUPONDB.clear()
    coupon_data._COUPONDB.update(copy.deepcopy(coupon_data._SEED))
