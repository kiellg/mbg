"""Router for checkout endpoints"""

from fastapi import APIRouter, Depends, status

from backend.app.dependencies import get_current_user
from backend.app.schemas.checkout import CheckoutRequest
from backend.app.schemas.order import OrderResponse
from backend.app.services import checkout_service

router = APIRouter(prefix="/checkout", tags=["checkout"])

@router.post("/{cart_id}", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    cart_id: int,
    payload: CheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    return checkout_service.checkout(
        cart_id=cart_id,
        customer_id=current_user["user_id"],
        delivery_method=payload.delivery_method
    )
