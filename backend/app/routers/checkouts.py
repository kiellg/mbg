"""Router for checkout endpoints"""

from typing import Optional

from fastapi import APIRouter, Depends, Header, Request, status

from app.dependencies import get_current_user
from app.schemas.checkout import CheckoutRequest
from app.schemas.coupon import CouponRecord
from app.schemas.order import OrderResponse
from app.services import checkout_service, coupon_service
from app.services.role_service import require_admin

router = APIRouter(prefix="/checkout", tags=["checkout"])


def get_session_token(
        request: Request,
        session_token: Optional[str] = Header(default=None),
) -> Optional[str]:
    """Return session token from header or cookie."""
    if session_token:
        return session_token

    return request.cookies.get("session_token")


def authenticate_admin(
        request: Request,
        session_token: Optional[str] = Header(default=None),
):
    """Authenticate the user and ensure they are an admin."""
    return require_admin(get_session_token(request, session_token))


@router.get("/debug/coupons", response_model=list[CouponRecord])
def debug_coupons(
    request: Request,
    session_token: Optional[str] = Header(default=None),
):
    """Return live discount codes for admin debugging."""
    authenticate_admin(request, session_token)
    return coupon_service.list_coupons()

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
        is_scheduled=payload.is_scheduled,
        scheduled_time=payload.scheduled_time,
    )
