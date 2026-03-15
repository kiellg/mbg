"""Schemas for delivery status and details responses"""
from pydantic import BaseModel
from backend.app.schemas.order import OrderStatus, DeliveryMethod

class DeliveryStatusResponse(BaseModel):
    """Response schema for delivery status and ETA"""
    order_id: str
    status: OrderStatus
    delivery_time: str
    delivery_time_actual: float
    delivery_delay: float

class DeliveryDetailsResponse(BaseModel):
    """Response schema for driver and delivery details"""
    order_id: str
    driver_name: str
    delivery_method: DeliveryMethod
    delivery_distance: float
    route_taken: str

class AssignedDeliveryResponse(BaseModel):
    order_id: str
    customer_address: str
    customer_phone: str
    driver_name: str
    delivery_method: DeliveryMethod
    status: str
    estimated_arrival: str
