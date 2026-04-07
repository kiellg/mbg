"""Router for checkout endpoints"""

from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user
from app.schemas.checkout import CheckoutRequest
from app.schemas.order import OrderResponse
from app.services import checkout_service

router = APIRouter(prefix="/checkout", tags=["checkout"])

@router.post("/{restaurant_id}", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    restaurant_id: int,
    payload: CheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """Endpoint to convert a cart into an order. Returns the created order details."""
    return checkout_service.checkout(
        restaurant_id = restaurant_id,
        customer_id=current_user["user_id"],
        delivery_method=payload.delivery_method,
        coupon_code=payload.coupon_code,
    )
