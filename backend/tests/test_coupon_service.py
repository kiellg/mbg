"""Unit tests for coupon_service.py."""

from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.repositories import coupon_repo
from app.schemas.coupon import CouponCreateRequest, CouponUpdateRequest
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
    coupon_repo.put_coupon_record("BROKEN", {
        "code": "BROKEN",
        "discount_type": "percentage",
        "percent_off": 150,
        "amount_off_cents": None,
        "minimum_subtotal_cents": 0,
        "expires_at": "2099-12-31T23:59:59+00:00",
        "is_active": True,
    })

    with pytest.raises(HTTPException) as exc:
        coupon_service.get_coupon_snapshot_for_checkout("BROKEN", Decimal("49.99"))

    assert exc.value.status_code == 500
    assert exc.value.detail == "Invalid coupon configuration for code 'BROKEN'."


def test_create_coupon_normalizes_code_and_stores_record():
    """New coupon codes should be normalized before being stored."""
    result = coupon_service.create_coupon(
        CouponCreateRequest(
            code=" save25 ",
            discount_type="percentage",
            percent_off=25,
            minimum_subtotal_cents=5000,
        )
    )

    assert result["code"] == "SAVE25"
    assert result["percent_off"] == 25
    assert coupon_repo.get_coupon_by_code("SAVE25")["minimum_subtotal_cents"] == 5000


def test_create_coupon_rejects_duplicate_code():
    """Creating a coupon with an existing code should fail."""
    with pytest.raises(HTTPException) as exc:
        coupon_service.create_coupon(
            CouponCreateRequest(
                code="save10",
                discount_type="percentage",
                percent_off=10,
            )
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Coupon code already exists."


def test_get_coupon_returns_normalized_match():
    """Looking up a coupon by code should ignore case and whitespace."""
    result = coupon_service.get_coupon(" save10 ")

    assert result["code"] == "SAVE10"
    assert result["discount_type"] == "percentage"


def test_update_coupon_updates_fields_without_changing_code():
    """Updating a coupon should preserve the stored code and merge mutable fields."""
    result = coupon_service.update_coupon(
        "save10",
        CouponUpdateRequest(
            percent_off=15,
            minimum_subtotal_cents=2500,
        ),
    )

    assert result["code"] == "SAVE10"
    assert result["percent_off"] == 15
    assert result["minimum_subtotal_cents"] == 2500


def test_deactivate_coupon_sets_coupon_inactive():
    """Deactivating a coupon should keep the record but mark it inactive."""
    result = coupon_service.deactivate_coupon("save10")

    assert result["code"] == "SAVE10"
    assert result["is_active"] is False


def test_delete_coupon_removes_coupon_record():
    """Deleting a coupon should remove it from the live store."""
    coupon_service.delete_coupon("save10")

    assert coupon_repo.get_coupon_by_code("SAVE10") is None
