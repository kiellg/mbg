"""Router for delivery endpoints"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from backend.app.schemas.delivery import DeliveryStatusResponse, DeliveryDetailsResponse
import backend.app.services.delivery_service as delivery_service
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
