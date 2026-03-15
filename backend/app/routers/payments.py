#pylint: disable=unused-argument
"""Router for payment endpoints."""

from fastapi import APIRouter, Depends, status

from backend.app.dependencies import get_current_user
from backend.app.schemas.payment import PaymentRequest, PaymentResponse, PaymentReceipt
from backend.app.services import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])

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