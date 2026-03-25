#pylint: disable=unused-argument
"""Router for payment endpoints."""

from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user
from app.schemas.payment import (
    PaymentRequest,
    PaymentResponse,
    PaymentReceipt,
    SavedPaymentMethod,
    SavedPaymentMethodRequest,
)
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post(
    "/methods",
    response_model=SavedPaymentMethod,
    status_code=status.HTTP_201_CREATED,
)
def save_payment_method(
    payload: SavedPaymentMethodRequest,
    current_user: dict = Depends(get_current_user),
):
    """Customer saves a dummy payment method for future reuse."""
    return payment_service.save_payment_method(
        customer_id=current_user["user_id"],
        payload=payload,
    )

@router.get("/methods", response_model=list[SavedPaymentMethod])
def get_saved_payment_methods(
    current_user: dict = Depends(get_current_user),
):
    """Customer retrieves their saved payment methods."""
    return payment_service.get_saved_payment_methods(
        customer_id=current_user["user_id"],
    )

@router.post("/{order_id}",
             response_model=PaymentResponse,
             status_code=status.HTTP_201_CREATED,
             )
def process_payment(
    order_id: str,
    payload: PaymentRequest,
    current_user: dict = Depends(get_current_user),
):
    """Customer submits payment details to finalize their order"""

    return payment_service.process_payment(
        order_id=order_id,
        customer_id=current_user["user_id"],
        payload=payload,
    )

@router.get(
    "/{order_id}/receipt",
    response_model=PaymentReceipt,
)
def get_receipt(
    order_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Customer retrieves their receipt after a successful payment."""
    return payment_service.get_receipt(
        order_id=order_id,
        customer_id=current_user["user_id"]
    )

@router.post(
    "/{order_id}/saved/{saved_method_id}",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def process_payment_with_saved_methods(
    order_id: str,
    saved_method_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Customer pays using a previously saved payment method."""
    return payment_service.process_payment_with_saved_methods(
        order_id=order_id,
        customer_id=current_user["user_id"],
        saved_method_id=saved_method_id,
    )
