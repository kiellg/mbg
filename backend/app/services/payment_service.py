"""Service layer for payment processing."""

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException

from app.repositories import order_repo, payment_repo, user_repo
from app.schemas.payment import (
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
    PaymentReceipt,
    SavedPaymentMethod,
    SavedPaymentMethodRequest,
)
from app.services import notification_service

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

    if status == PaymentStatus.ACCEPTED:
        updated_order = order_repo.set_order_status(order_id, "Cooking")
        if updated_order:
            notification_service.create_order_status_changed_notification(
                updated_order["order_id"],
                updated_order["status"],
            )

    return _build_payment_response(record)

def get_receipt(order_id: str, customer_id: str) -> PaymentReceipt:
    """Retrieve the payment receipt for a successfully paid order."""
    order = order_repo.get_order_record(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order["customer_id"] != customer_id:
        raise HTTPException(status_code=403,
                            detail="Not authorized to view this receipt.")

    record = payment_repo.get_payment_by_order_id(order_id)
    if record is None or record["status"] != PaymentStatus.ACCEPTED.value:
        raise HTTPException(status_code=404,
                            detail="No accepted payment found for this order.")

    return PaymentReceipt(
        payment_id=record["payment_id"],
        order_id=order_id,
        amount=Decimal(record["amount"]),
        last4=record["last4"],
        cardholder_name=record["cardholder_name"],
        timestamp=datetime.fromisoformat(record["timestamp"]),
    )

def save_payment_method(
    customer_id: str,
    payload: SavedPaymentMethodRequest,
) -> SavedPaymentMethod:
    """Validate card details, tokenize, and save for future use"""
    _validate_card_number(payload.card_number)
    _validate_expiry_date(payload.expiry_date)
    _validate_cvv(payload.cvv)

    card_token = payment_repo.create_card_token(payload.card_number)

    method = user_repo.save_payment_method(
        customer_id=customer_id,
        card_token=card_token,
        last4=payload.card_number[-4:],
        expiry_date=payload.expiry_date,
        cardholder_name=payload.cardholder_name,
        nickname=payload.nickname,
    )

    if method is None:
        raise HTTPException(status_code=404, detail="Customer profile not found.")

    return SavedPaymentMethod(
        saved_method_id=method["saved_method_id"],
        last4=method["last4"],
        expiry_date=method["expiry_date"],
        cardholder_name=method["cardholder_name"],
        nickname=method["nickname"],
    )

def get_saved_payment_methods(customer_id: str):
    """Return all saved payment methods for a customer."""
    methods = user_repo.get_saved_payment_methods(customer_id)
    return [
        SavedPaymentMethod(
            saved_method_id=m["saved_method_id"],
            last4=m["last4"],
            expiry_date=m["expiry_date"],
            cardholder_name=m["cardholder_name"],
            nickname=m["nickname"],
        )
        for m in methods
    ]

def process_payment_with_saved_methods(
    order_id: str,
    customer_id: str,
    saved_method_id: str,
):
    """Process payment using a previously saved payment method."""
    methods = user_repo.get_saved_payment_methods(customer_id)
    method = next(
        (m for m in methods if m["saved_method_id"] == saved_method_id), None
    )
    if method is None:
        raise HTTPException(status_code=404, detail="Saved payment method not found.")

    card_number = payment_repo.resolve_card_token(method["card_token"])
    if card_number is None:
        raise HTTPException(status_code=500, detail="Card token could not be resolved.")

    payload = PaymentRequest(
        card_number=card_number,
        expiry_date=method["expiry_date"],
        cvv="000",
        cardholder_name=method["cardholder_name"],
    )

    return process_payment(order_id, customer_id, payload)
