"""Service layer for internal discount code lookup and validation."""

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from pydantic import ValidationError

from app.repositories import coupon_repo
from app.schemas.coupon import CouponRecord, CouponSnapshot


def normalize_coupon_code(coupon_code: str | None) -> str | None:
    """Normalize the customer provided coupon code."""
    if coupon_code is None:
        return None

    normalized = coupon_code.strip().upper()
    if not normalized:
        return None

    return normalized


def get_coupon_snapshot_for_checkout(
    coupon_code: str | None,
    subtotal: Decimal,
) -> dict | None:
    """Validate a checkout coupon and return the snapshot to store on the order."""
    normalized_code = normalize_coupon_code(coupon_code)
    if normalized_code is None:
        return None

    raw_coupon = coupon_repo.get_coupon_by_code(normalized_code)
    if raw_coupon is None:
        raise HTTPException(status_code=400, detail="Invalid coupon code.")

    try:
        coupon = CouponRecord.model_validate(raw_coupon)
    except ValidationError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid coupon configuration for code '{normalized_code}'.",
        ) from exc

    if not coupon.is_active:
        raise HTTPException(status_code=400, detail="Coupon code is inactive.")

    now = datetime.now(timezone.utc)
    if coupon.expires_at is not None and coupon.expires_at <= now:
        raise HTTPException(status_code=400, detail="Coupon code has expired.")

    minimum_subtotal = Decimal(coupon.minimum_subtotal_cents) / Decimal("100")
    if subtotal < minimum_subtotal:
        raise HTTPException(
            status_code=400,
            detail="Order subtotal does not meet the coupon minimum.",
        )

    snapshot = CouponSnapshot.model_validate(coupon.model_dump())
    return snapshot.model_dump(mode="json")
