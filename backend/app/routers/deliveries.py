"""Router for delivery endpoints"""
from typing import Optional
from fastapi import APIRouter, Header

from backend.app.schemas.delivery import (
    DeliveryStatusResponse,
    DeliveryDetailsResponse,
    AssignedDeliveryResponse
)
from backend.app.services import delivery_service
from backend.app.services.role_service import require_driver
from backend.app.schemas.order import OrderStatus

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

@router.patch("/{order_id}/status")
def update_delivery_status(
    order_id: str,
    body: dict,
    session_token: Optional[str] = Header(default=None),
):
    """Driver updates delivery status"""
    require_driver(session_token)
    return delivery_service.update_delivery_status(order_id, body["status"])

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
