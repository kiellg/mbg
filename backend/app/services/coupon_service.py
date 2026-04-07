"""Service layer for internal discount code lookup and validation."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from fastapi import HTTPException
from pydantic import ValidationError

from app.repositories import coupon_repo
from app.schemas.coupon import (
    CouponCreateRequest,
    CouponRecord,
    CouponResponse,
    CouponSnapshot,
    CouponUpdateRequest,
)


def normalize_coupon_code(coupon_code: str | None) -> str | None:
    """Normalize the customer provided coupon code."""
    if coupon_code is None:
        return None

    normalized = coupon_code.strip().upper()
    if not normalized:
        return None

    return normalized


def _raise_invalid_coupon_data(exc: ValidationError) -> None:
    """Raise a 400 with the first coupon validation error message."""
    message = exc.errors()[0].get("msg", "Invalid coupon data.")
    raise HTTPException(status_code=400, detail=message)


def _validate_coupon_record(raw_coupon: dict, code: str) -> CouponRecord:
    """Validate a raw coupon record and raise a clear error when malformed."""
    try:
        return CouponRecord.model_validate(raw_coupon)
    except ValidationError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid coupon configuration for code '{code}'.",
        ) from exc


def _require_coupon_code(coupon_code: str | None) -> str:
    """Normalize and require a non-blank coupon code."""
    normalized_code = normalize_coupon_code(coupon_code)
    if normalized_code is None:
        raise HTTPException(status_code=400, detail="Coupon code is required.")
    return normalized_code


def _get_coupon_record_or_404(coupon_code: str) -> dict:
    """Return a coupon record or raise 404 when it is missing."""
    record = coupon_repo.get_coupon_by_code(coupon_code)
    if record is None:
        raise HTTPException(status_code=404, detail="Coupon not found.")
    return record


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

    coupon = _validate_coupon_record(raw_coupon, normalized_code)

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


def list_coupons() -> list[dict[str, Any]]:
    """Return all validated coupons for admin management or debug visibility."""
    coupons = []
    for raw_coupon in coupon_repo.list_coupons():
        code = raw_coupon.get("code", "<unknown>")
        coupon = _validate_coupon_record(raw_coupon, code)
        coupons.append(CouponResponse.model_validate(coupon.model_dump()).model_dump(mode="json"))
    return coupons


def list_coupons_for_debug() -> list[dict[str, Any]]:
    """Backward-compatible alias for the guarded debug route."""
    return list_coupons()


def get_coupon(coupon_code: str) -> dict[str, Any]:
    """Return a single coupon by code for admin management."""
    normalized_code = _require_coupon_code(coupon_code)
    coupon = _validate_coupon_record(
        _get_coupon_record_or_404(normalized_code),
        normalized_code,
    )
    return CouponResponse.model_validate(coupon.model_dump()).model_dump(mode="json")


def create_coupon(payload: CouponCreateRequest) -> dict[str, Any]:
    """Create a coupon for admin management."""
    normalized_code = _require_coupon_code(payload.code)
    if coupon_repo.get_coupon_by_code(normalized_code) is not None:
        raise HTTPException(status_code=400, detail="Coupon code already exists.")

    raw_coupon = payload.model_dump(mode="json")
    raw_coupon["code"] = normalized_code

    created = coupon_repo.create_coupon_record(raw_coupon)
    return CouponResponse.model_validate(created).model_dump(mode="json")


def update_coupon(coupon_code: str, payload: CouponUpdateRequest) -> dict[str, Any]:
    """Update mutable coupon fields while keeping the code immutable."""
    normalized_code = _require_coupon_code(coupon_code)
    existing = _get_coupon_record_or_404(normalized_code)
    patch = payload.model_dump(exclude_unset=True, mode="json")
    if not patch:
        raise HTTPException(status_code=400, detail="No fields provided.")

    merged = {**existing, **patch, "code": normalized_code}

    try:
        coupon = CouponResponse.model_validate(merged)
    except ValidationError as exc:
        _raise_invalid_coupon_data(exc)

    updated = coupon_repo.update_coupon_record(normalized_code, coupon.model_dump(mode="json"))
    if updated is None:
        raise HTTPException(status_code=404, detail="Coupon not found.")
    return CouponResponse.model_validate(updated).model_dump(mode="json")


def deactivate_coupon(coupon_code: str) -> dict[str, Any]:
    """Deactivate an existing coupon."""
    normalized_code = _require_coupon_code(coupon_code)
    _get_coupon_record_or_404(normalized_code)

    updated = coupon_repo.deactivate_coupon_record(normalized_code)
    if updated is None:
        raise HTTPException(status_code=404, detail="Coupon not found.")
    return CouponResponse.model_validate(updated).model_dump(mode="json")


def delete_coupon(coupon_code: str) -> None:
    """Delete a coupon from the live store."""
    normalized_code = _require_coupon_code(coupon_code)
    deleted = coupon_repo.delete_coupon_record(normalized_code)
    if not deleted:
        raise HTTPException(status_code=404, detail="Coupon not found.")
