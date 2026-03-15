"""Service layer for delivery status and details"""
from fastapi import HTTPException
from backend.app.repositories import order_repo
from backend.app.schemas.delivery import (
    DeliveryStatusResponse,
    DeliveryDetailsResponse,
    AssignedDeliveryResponse
)
from backend.app.schemas.order import DeliveryMethod, OrderStatus

VALID_TRANSITIONS = {
    OrderStatus.PENDING: [OrderStatus.COOKING, OrderStatus.CANCELLED],
    OrderStatus.COOKING: [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.CANCELLED],
    OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: [],
}

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

def update_delivery_status(order_id: str, new_status: str) -> dict:
    """Driver updates delivery status with transition validation"""
    order = order_repo.get_order_record(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    current = OrderStatus(order["status"])
    next_status = OrderStatus(new_status)

    if next_status not in VALID_TRANSITIONS[current]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {current.value} to {next_status.value}",
        )

    order_repo.set_order_status(order_id, new_status)
    return {"order_id": order_id, "status": new_status}

def get_assigned_deliveries(driver_name: str) -> list[AssignedDeliveryResponse]:
    """Return all orders assigned to the requesting driver"""
    orders = order_repo.get_orders_assigned_to_driver(driver_name)
    return [
        AssignedDeliveryResponse(
            order_id=order["order_id"],
            customer_address=order["delivery_address"],
            customer_phone=order.get("customer_phone", ""),
            driver_name=order["driver_name"],
            delivery_method=DeliveryMethod(order.get("delivery_method", "walk")),
            status=order["status"],
            estimated_arrival=order.get("delivery_time", ""),
        )
        for order in orders
    ]
