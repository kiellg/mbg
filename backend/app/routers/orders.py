"""Router for editable pending order endpoints."""

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.order import OrderResponse, PendingOrderUpdate
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.patch("/{order_id}", response_model=OrderResponse)
def update_pending_order(
    order_id: str,
    payload: PendingOrderUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update an editable pending order for the logged-in user."""
    return order_service.update_pending_order(
        order_id=order_id,
        user_id=current_user["user_id"],
        payload=payload,
    )
