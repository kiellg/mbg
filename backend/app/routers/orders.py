"""Router for editable pending order endpoints."""

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.order import OrderResponse, PendingOrderUpdate, OrderCreate
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

@router.post("", response_model=OrderResponse)
def create_order(payload: OrderCreate):
    """Create a new order"""
    return order_service.create_order(payload)

@router.get("", response_model=list[OrderResponse])
def list_order():
    """List all orders"""
    return order_service.list_orders()
