"""Router for delivery endpoints"""
from typing import Optional
from fastapi import APIRouter, Header

from backend.app.schemas.delivery import DeliveryStatusResponse, DeliveryDetailsResponse
from backend.app.services import delivery_service
from backend.app.services.role_service import require_driver

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/assigned")
def get_assigned_deliveries(session_token: Optional[str] = Header(default=None)):
    """Drivers can view assigned deliveries"""
    require_driver(session_token)
    return {"message": "Assigned deliveries"}

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
