"""Router for delivery endpoints"""
from typing import Optional
from fastapi import APIRouter, Header

from backend.app.schemas.delivery import DeliveryStatusResponse, DeliveryDetailsResponse, AssignedDeliveryResponse
from backend.app.services import delivery_service
from backend.app.services.role_service import require_driver
from backend.app.repositories.user_repo import get_user_by_id

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/assigned", response_model=list[AssignedDeliveryResponse])
def get_assigned_deliveries(session_token: Optional[str] = Header(default=None)):
    user = require_driver(session_token)
    user_id = user["user_id"]
    user_record = get_user_by_id(user_id)
    return delivery_service.get_assigned_deliveries(user_record["name"])

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
