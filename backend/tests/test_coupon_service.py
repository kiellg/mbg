"""Unit tests for coupon_service.py."""

from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.data import coupon_data
from app.repositories import coupon_repo
from app.services import coupon_service


@pytest.fixture(autouse=True)
def reset_coupon_state():
    """Reset seeded coupon records before and after each test."""
    coupon_repo.reset_coupons()
    yield
    coupon_repo.reset_coupons()


def test_get_coupon_snapshot_for_checkout_returns_percentage_snapshot():
    """A valid percentage coupon should return the stored snapshot."""
    snapshot = coupon_service.get_coupon_snapshot_for_checkout(" save10 ", Decimal("49.99"))

    assert snapshot["code"] == "SAVE10"
    assert snapshot["discount_type"] == "percentage"
    assert snapshot["percent_off"] == 10


def test_get_coupon_snapshot_for_checkout_returns_none_for_blank_code():
    """Blank coupon codes should be treated as absent."""
    snapshot = coupon_service.get_coupon_snapshot_for_checkout("   ", Decimal("49.99"))

    assert snapshot is None


def test_get_coupon_snapshot_for_checkout_rejects_inactive_code():
    """Inactive coupon codes should be rejected."""
    with pytest.raises(HTTPException) as exc:
        coupon_service.get_coupon_snapshot_for_checkout("INACTIVE10", Decimal("49.99"))

    assert exc.value.status_code == 400
    assert exc.value.detail == "Coupon code is inactive."


def test_get_coupon_snapshot_for_checkout_rejects_expired_code():
    """Expired coupon codes should be rejected."""
    with pytest.raises(HTTPException) as exc:
        coupon_service.get_coupon_snapshot_for_checkout("EXPIRED5", Decimal("49.99"))

    assert exc.value.status_code == 400
    assert exc.value.detail == "Coupon code has expired."


def test_get_coupon_snapshot_for_checkout_rejects_below_minimum():
    """Minimum subtotal must be met before a coupon can be applied at checkout."""
    with pytest.raises(HTTPException) as exc:
        coupon_service.get_coupon_snapshot_for_checkout("MIN60", Decimal("49.99"))

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order subtotal does not meet the coupon minimum."


def test_get_coupon_snapshot_for_checkout_fails_loudly_for_bad_seed_config():
    """Malformed seeded coupon data should raise a clear server-side validation error."""
    coupon_data._COUPONDB["BROKEN"] = {
        "code": "BROKEN",
        "discount_type": "percentage",
        "percent_off": 150,
        "amount_off_cents": None,
        "minimum_subtotal_cents": 0,
        "expires_at": "2099-12-31T23:59:59+00:00",
        "is_active": True,
    }

    with pytest.raises(HTTPException) as exc:
        coupon_service.get_coupon_snapshot_for_checkout("BROKEN", Decimal("49.99"))

    assert exc.value.status_code == 500
    assert exc.value.detail == "Invalid coupon configuration for code 'BROKEN'."
