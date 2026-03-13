"""Service layer for delivery status and details"""
from fastapi import HTTPException
from backend.app.repositories import order_repo
from backend.app.schemas.delivery import DeliveryStatusResponse, DeliveryDetailsResponse
from backend.app.schemas.order import DeliveryMethod

def get_delivery_status(order_id: str) -> DeliveryStatusResponse:
    """Return delivery status and ETA for a given order"""
    order = order_repo.get_order_record(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return DeliveryStatusResponse(
        order_id=order["order_id"],
        status=order["status"],
        delivery_time=order.get("delivery_time", ""),
        delivery_time_actual=order.get("delivery_time_actual", 0.0),
        delivery_delay=order.get("delivery_delay", 0.0),
    )

def get_delivery_details(order_id: str) -> DeliveryDetailsResponse:
    """Return driver name and delivery method for a given order"""
    order = order_repo.get_order_record(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return DeliveryDetailsResponse(
        order_id=order["order_id"],
        driver_name=order.get("driver_name") or "Unassigned",
        delivery_method=DeliveryMethod(order.get("delivery_method", "walk")),
        delivery_distance=order.get("delivery_distance", 0.0),
        route_taken=order.get("route_taken", ""),
    )
