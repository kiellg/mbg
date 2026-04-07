"""Internal schemas for discount code validation and snapshots."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DiscountType(str, Enum):
    """Supported discount code types."""

    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


class CouponBase(BaseModel):
    """Shared fields for coupon configuration and snapshots."""

    model_config = ConfigDict(
        validate_assignment=True,
    )

    code: str
    discount_type: DiscountType
    percent_off: Optional[int] = Field(default=None)
    amount_off_cents: Optional[int] = Field(default=None, gt=0)
    minimum_subtotal_cents: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_discount_fields(self):
        """Ensure the configured discount matches the selected type."""
        if self.discount_type == DiscountType.PERCENTAGE:
            if self.percent_off is None:
                raise ValueError("percent_off is required for percentage discounts")
            if self.percent_off <= 0 or self.percent_off > 100:
                raise ValueError("percent_off must be greater than 0 and at most 100")
            if self.amount_off_cents is not None:
                raise ValueError("amount_off_cents must be omitted for percentage discounts")
            return self

        if self.amount_off_cents is None:
            raise ValueError("amount_off_cents is required for fixed amount discounts")
        if self.amount_off_cents <= 0:
            raise ValueError("amount_off_cents must be greater than 0")
        if self.percent_off is not None:
            raise ValueError("percent_off must be omitted for fixed amount discounts")
        return self


class CouponRecord(CouponBase):
    """Validated coupon configuration loaded from the seeded data store."""

    expires_at: Optional[datetime] = None
    is_active: bool = True


class CouponSnapshot(CouponBase):
    """Immutable coupon rule snapshot stored on an order."""


class CouponCreateRequest(CouponRecord):
    """Schema for creating a coupon through the admin API."""


class CouponUpdateRequest(BaseModel):
    """Schema for updating coupon fields except code."""

    discount_type: Optional[DiscountType] = None
    percent_off: Optional[int] = Field(default=None)
    amount_off_cents: Optional[int] = Field(default=None, gt=0)
    minimum_subtotal_cents: Optional[int] = Field(default=None, ge=0)
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class CouponResponse(CouponRecord):
    """Schema returned by admin coupon CRUD endpoints."""
