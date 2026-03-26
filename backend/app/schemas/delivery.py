"""Schemas for delivery status/details requests and responses"""
from pydantic import BaseModel, ConfigDict
from app.schemas.order import OrderStatus, DeliveryMethod

class AssignDriverRequest(BaseModel):
    """Request schema for assigning a driver to an order"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "driver_id": "driver-123",
                "delivery_method": "bike",
            }
        }
    )

    driver_id: str
    delivery_method: DeliveryMethod

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
    driver_id: str
    delivery_method: DeliveryMethod
    delivery_distance: float
    route_taken: str

class AssignedDeliveryResponse(BaseModel):
    """Response schema for orders assigned to a driver"""
    order_id: str
    customer_address: str
    customer_phone: str
    driver_name: str
    driver_id: str
    delivery_method: DeliveryMethod
    status: str
    estimated_arrival: str
