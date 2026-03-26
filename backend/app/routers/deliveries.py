"""Router for delivery endpoints"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.schemas.delivery import (
    AssignDriverRequest,
    DeliveryStatusResponse,
    DeliveryDetailsResponse,
    AssignedDeliveryResponse
)
from app.schemas.order import OrderResponse
from app.services import delivery_service
from app.services.role_service import require_driver, require_manager
from app.schemas.order import OrderStatus

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/assigned", response_model=list[AssignedDeliveryResponse])
def get_assigned_deliveries(session_token: Optional[str] = Header(default=None)):
    """Driver views all orders currently assigned to them"""
    user = require_driver(session_token)
    return delivery_service.get_assigned_deliveries(user["user_id"])

@router.get("/{order_id}/status", response_model=DeliveryStatusResponse)
def get_delivery_status(order_id: str):
    """Customer views current delivery status and ETA"""
    return delivery_service.get_delivery_status(order_id)

@router.get("/{order_id}/details", response_model=DeliveryDetailsResponse)
def get_delivery_details(order_id: str):
    """Customer views driver name and delivery method"""
    return delivery_service.get_delivery_details(order_id)


@router.patch("/{order_id}/driver")
def assign_driver_to_order(
    order_id: str,
    payload: AssignDriverRequest,
    session_token: Optional[str] = Header(default=None),
):
    """Manager assigns a driver to an order"""
    manager = require_manager(session_token)

    return delivery_service.assign_driver_to_order(
        order_id=order_id,
        driver_id=payload.driver_id,
        manager_id=manager["user_id"],
        delivery_method=payload.delivery_method.value
    )


@router.patch("/{order_id}/status")
def update_delivery_status(
    order_id: str,
    body: Optional[dict] = None,
    session_token: Optional[str] = Header(default=None),
):
    """Driver updates delivery status"""
    require_driver(session_token or "")

    if body is None:
        return {"order_id": order_id, "message": "Delivery status updated"}

    status = body.get("status")
    if status is None:
        raise HTTPException(status_code=400, detail="Missing status")

    return delivery_service.update_delivery_status(order_id, status)

@router.get("/kitchen/{restaurant_id}",
            response_model=list[OrderResponse])
def get_kitchen_queue(
    restaurant_id: int,
    session_token: Optional[str] = Header(default=None)
):
    """Manager views orders ready for preparation for their restaurant"""
    manager =  require_manager(session_token)
    return delivery_service.get_kitchen_queue(
        restaurant_id = restaurant_id,
        manager_id = manager["user_id"],
    )

@router.patch("/{order_id}/status/out-for-delivery")
def mark_order_out_for_delivery(
    order_id: str,
    session_token: Optional[str] = Header(default=None),
):
    """Driver marks an order as Out for Delivery"""
    require_driver(session_token)
    return delivery_service.update_delivery_status(order_id, OrderStatus.OUT_FOR_DELIVERY.value)


@router.patch("/{order_id}/status/delivered")
def mark_order_delivered(
    order_id: str,
    session_token: Optional[str] = Header(default=None),
):
    """Driver marks an order as Delivered"""
    require_driver(session_token)
    return delivery_service.update_delivery_status(order_id, OrderStatus.DELIVERED.value)

@router.patch("/{order_id}/status/cancelled")
def mark_order_cancelled(
    order_id: str,
    session_token: Optional[str] = Header(default=None),
):
    """Manager marks an order as Cancelled"""
    require_manager(session_token)
    return delivery_service.update_delivery_status(order_id, OrderStatus.CANCELLED.value)
