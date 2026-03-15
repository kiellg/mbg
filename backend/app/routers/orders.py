"""Router for delivery endpoints"""
#pylint: disable=duplicate-code, unused-import

from typing import Optional
from fastapi import APIRouter, Header

from backend.app.services.role_service import require_driver

router = APIRouter(prefix="/orders", tags=["orders"])

# @router.get("/assigned")
# def get_assigned_deliveries(session_token: Optional[str] = Header(default=None)):
#     """Drivers can view assigned deliveries"""
#     require_driver(session_token)
#     return {"message": "Assigned deliveries"}

# @router.patch("/{order_id}/status")
# def update_delivery_status(
#     order_id: str, 
#     session_token: Optional[str] = Header(default=None),
# ):
#     """Drivers can update delivery status"""
#     require_driver(session_token)
#     return{
#         "order_id": order_id,
#         "message": "Delivery status updated",
#     }
