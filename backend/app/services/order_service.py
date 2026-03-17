"""Service layer for order management, handling business logic 
and interactions with the order repository."""
from decimal import Decimal
from types import SimpleNamespace
from fastapi import HTTPException
from backend.app.repositories import order_repo
from backend.app.schemas.order import (
    DeliveryMethod,
    OrderCreate,
    OrderResponse,
    OrderItemResponse,
    OrderUpdate
)
from backend.app.services import notification_service
from backend.app.services.pricing_service import PricingService

def _validate_order_is_pending(order: dict) -> None:
    """Raise an HTTPException when an order is not editable."""
    if order["status"] != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending orders can be modified or cancelled.",
        )

def _calculate_totals_patch(order: dict) -> dict:
    """Calculate and return stored totals for an order."""
    pricing_order = SimpleNamespace(
        items=[
            SimpleNamespace(
                quantity=item["quantity"],
                item_price=Decimal(str(item["item_price"])),
            )
            for item in order.get("items", [])
        ],
        delivery_method=order["delivery_method"],
        subtotal=Decimal("0.00"),
        tax=Decimal("0.00"),
        delivery_fee=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    PricingService.calculate_totals(pricing_order)
    return {
        "subtotal": pricing_order.subtotal,
        "tax": pricing_order.tax,
        "delivery_fee": pricing_order.delivery_fee,
        "total": pricing_order.total,
    }

def _build_order_response(order: dict) -> OrderResponse:
    """Helper to build an OrderResponse from a raw order dict."""
    item_responses = []

    for item in order.get("items", []):
        item_responses.append(
            OrderItemResponse(
                order_item_id=item["order_item_id"],
                order_id=item["order_id"],
                quantity=item["quantity"],
                item_price=Decimal(str(item["item_price"])),
            )
        )

    response = OrderResponse(
        order_id=order["order_id"],
        status=order["status"],
        customer_id=order["customer_id"],
        restaurant_id=order["restaurant_id"],
        delivery_address=order["delivery_address"],
        delivery_method=DeliveryMethod(order["delivery_method"]),
        items=item_responses,
        subtotal=Decimal(str(order["subtotal"])),
        tax=Decimal(str(order["tax"])),
        delivery_fee=Decimal(str(order["delivery_fee"])),
        total=Decimal(str(order["total"])),
    )
    return response

def create_order(payload: OrderCreate) -> OrderResponse:
    """Create a new order and return the created order details."""
    items= [
        {
            "quantity": item.quantity,
            "item_price": item.item_price,
        }
        for item in payload.items
    ]

    order = order_repo.create_order_record(
        customer_id=payload.customer_id,
        restaurant_id=payload.restaurant_id,
        delivery_address=payload.delivery_address,
        items=items,
        delivery_method=payload.delivery_method.value,
        status=payload.status.value,
    )

    stored_order = order_repo.update_order_record(order["order_id"], _calculate_totals_patch(order))
    if not stored_order:
        raise HTTPException(status_code=500, detail="Failed to update order")

    notification_service.create_order_placed_notification(stored_order["order_id"])
    return _build_order_response(stored_order)

def get_order(order_id: str) -> OrderResponse:
    """Retrieve a single order by ID"""
    order = order_repo.get_order_record(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return _build_order_response(order)

def list_orders() -> list[OrderResponse]:
    """List all orders"""
    orders = order_repo.list_order_records()
    return [_build_order_response(order) for order in orders]

def update_order(order_id: str, payload: OrderUpdate) -> OrderResponse:
    """Apply a partial update to an existing order"""
    order = order_repo.get_order_record(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    previous_status = order["status"]
    patch: dict = {}

    if payload.status is not None:
        patch["status"] = payload.status.value
    if payload.delivery_address is not None:
        patch["delivery_address"] = payload.delivery_address
    if payload.delivery_method is not None:
        patch["delivery_method"] = payload.delivery_method.value
    if payload.items is not None:
        patch["items"] = [
            {
                "quantity": item.quantity,
                "item_price": item.item_price,
            }
            for item in payload.items
        ]

    if not patch:
        return _build_order_response(order)

    _validate_order_is_pending(order)
    patch.update(_calculate_totals_patch({**order, **patch}))

    updated_order = order_repo.update_order_record(order_id, patch)
    if not updated_order:
        raise HTTPException(status_code=500, detail="Failed to update order")

    if payload.status is not None and updated_order["status"] != previous_status:
        notification_service.create_order_status_changed_notification(
            updated_order["order_id"],
            updated_order["status"],
        )
    return _build_order_response(updated_order)

def cancel_order(order_id: str) -> OrderResponse:
    """Cancel an order by setting its status to Cancelled."""
    order = order_repo.get_order_record(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    _validate_order_is_pending(order)

    updated_order = order_repo.cancel_order_record(order_id)
    if not updated_order:
        raise HTTPException(status_code=500, detail="Failed to cancel order")

    notification_service.create_order_status_changed_notification(
        updated_order["order_id"],
        updated_order["status"],
    )
    return _build_order_response(updated_order)
