"""Service layer for delivery status and details"""
from fastapi import HTTPException
from backend.app.repositories import order_repo, restaurant_repo
from backend.app.schemas.delivery import (
    DeliveryStatusResponse,
    DeliveryDetailsResponse,
    AssignedDeliveryResponse
)
from backend.app.schemas.order import DeliveryMethod, OrderStatus, OrderResponse
from backend.app.services.order_service import _build_order_response
from backend.app.services import notification_service

VALID_TRANSITIONS = {
    OrderStatus.PENDING: [OrderStatus.COOKING],
    OrderStatus.COOKING: [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.CANCELLED],
    OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED],
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
        driver_id=order.get("driver_id") or "",
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

    updated_order = order_repo.set_order_status(order_id, new_status)
    if updated_order:
        notification_service.create_order_status_changed_notification(
            updated_order["order_id"],
            updated_order["status"],
        )

    response = {"order_id": order_id, "status": new_status}
    if next_status == OrderStatus.CANCELLED:
        response["message"] = f"Order has been cancelled. Refund of ${order['total']} is coming."
    return response

def get_assigned_deliveries(driver_id: str) -> list[AssignedDeliveryResponse]:
    """Return all orders assigned to the requesting driver"""
    orders = order_repo.get_orders_assigned_to_driver(driver_id)
    return [
        AssignedDeliveryResponse(
            order_id=order["order_id"],
            customer_address=order["delivery_address"],
            customer_phone=order.get("customer_phone", ""),
            driver_name=order.get("driver_name") or "Unassigned",
            driver_id=order["driver_id"],
            delivery_method=DeliveryMethod(order.get("delivery_method", "walk")),
            status=order["status"],
            estimated_arrival=order.get("delivery_time", ""),
        )
        for order in orders
    ]

def get_kitchen_queue(restaurant_id: int, manager_id: str) -> list[OrderResponse]:
    """Return Cooking orders for a specific restaurant."""
    restaurant = restaurant_repo.get_restaurant_record(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404,
                            detail="Restaurant not found")

    if restaurant.get("owner_id") != manager_id:
        raise HTTPException(status_code=403,
                            detail="Not authorized to view this restaurant's orders")

    all_orders = order_repo.list_order_records()
    return [
        _build_order_response(order)
        for order in all_orders
        if order["status"] == "Cooking"
        and order["restaurant_id"] == restaurant_id
    ]
