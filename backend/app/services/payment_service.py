"""Service layer for payment processing."""

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException

from backend.app.repositories import order_repo, payment_repo
from backend.app.schemas.payment import (
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
)

def _validate_card_number(card_number: str) -> None:
    """Card number must be exactly 16 digits."""
    if not card_number.isdigit() or len(card_number) != 16:
        raise HTTPException(
            status_code=400,
            detail="Invalid card number. Must be exactly 16 digits."
        )

def _validate_expiry_date(expiry_date: str) -> None:
    """Expiry date must be in MM/YY format and not expired."""
    if len(expiry_date) != 5 or expiry_date[2] != "/":
        raise HTTPException(
            status_code=400,
            detail="Invalid expiry date. Must be in MM/YY format."
        )
    
    month_str, year_str = expiry_date[:2], expiry_date[3:]

    if not month_str.isdigit() or not year_str.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid expiry date. Must be in MM/YY format."
        )
    
    month, year = int(month_str), int(year_str) + 2000

    if not 1 <= month <= 12:
        raise HTTPException(
            status_code=400,
            detail="Invalid expiry date. Month must be between 01 and 12."
        )
    
    now = datetime.now(timezone.utc)
    if year < now.year or (year == now.year and month < now.month):
        raise HTTPException(
            status_code=400,
            detail="Card has expired."
        )

def _validate_cvv(cvv: str) -> None:
    "CVV must be 3 or 4 digits"
    if not cvv.isdigit() or len(cvv) not in (3,4):
        raise HTTPException(
            status_code=400,
            detail="Invalid CVV. Must be 3 or 4 digits."
        )

def _validate_payment_info(payload: PaymentRequest) -> None:
    """Run all payment validations before."""
    _validate_card_number(payload.card_number)
    _validate_expiry_date(payload.expiry_date)
    _validate_cvv(payload.cvv)

def _simulate_payment(card_number: str) -> PaymentStatus:
    """Simulate accept/decline logic.
    In this case:
    - Cards ending in 0000 are always declined.
    - All other cards are accepted"""
    if card_number.endswith("0000"):
        return PaymentStatus.DECLINED
    return PaymentStatus.ACCEPTED

def _build_payment_response(record: dict) -> PaymentResponse:
    "Build a PaymentResponse from a raw payment record."
    return PaymentResponse(
        payment_id=record["payment_id"],
        order_id=record["order_id"],
        status=PaymentStatus(record["status"]),
        amount=Decimal(record["amount"]),
        last4=record["last4"],
        timestamp=datetime.fromisoformat(record["timestamp"]),
    )

def process_payment(
        order_id: str,
        customer_id: str,
        payload: PaymentRequest,
) -> PaymentResponse:
    """Validate payment info, simulate transaction, and update order on success."""
    order = order_repo.get_order_record(order_id)
    if order is None:
        raise HTTPException(status_code=404,
                            detail="Order not found")
    
    if order["customer_id"] != customer_id:
        raise HTTPException(status_code=403,
                            detail="Not authorized to pay for this order.")
    
    if order["status"] != "Pending":
        raise HTTPException(
            status_code=400,
            detail=f"Payment can only be made for Pending orders. "
                   f"Current status is '{order['status']}'.",
        )
    
    _validate_payment_info(payload)

    status = _simulate_payment(payload.card_number)
    last4 = payload.card_number[-4:]
    amount = order["total"]

    record = payment_repo.create_payment_record(
        order_id=order_id,
        status=status.value,
        amount=amount,
        last4=last4,
        cardholder_name=payload.cardholder_name,
    )

    return _build_payment_response(record)
