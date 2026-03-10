from decimal import Decimal
from fastapi import HTTPException
from backend.app.repositories import order_repo
from backend.app.schemas.order import (
    DeliveryMethod,
    OrderCreate,
    OrderResponse,
    OrderItemResponse,
    OrderUpdate
)
from backend.app.services.pricing_service import PricingService

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
        delivery_address=order["delivery_address"],
        delivery_method=DeliveryMethod(order["delivery_method"]),
        items=item_responses,
        subtotal=Decimal("0.00"),
        tax=Decimal("0.00"),
        delivery_fee=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    PricingService.calculate_totals(response)
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
        delivery_address=payload.delivery_address,
        items=items,
        delivery_method=payload.delivery_method.value,
        status=payload.status.value,
    )

    return _build_order_response(order)

def get_order(order_id: int) -> OrderResponse:
    """Retrieve a single order by ID"""
    order = order_repo.get_order_record(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return _build_order_response(order)

def list_orders() -> list[OrderResponse]:
    """List all orders"""
    orders = order_repo.list_order_records()
    return [_build_order_response(order) for order in orders]

def update_order(order_id: int, payload: OrderUpdate) -> OrderResponse:
    """Apply a partial update to an existing order"""
    order = order_repo.get_order_record(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

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
    
    updated_order = order_repo.update_order_record(order_id, patch)
    if not updated_order:
        raise HTTPException(status_code=500, detail="Failed to update order")
    return _build_order_response(updated_order)

def cancel_order(order_id: int) -> OrderResponse:
    """Cancel an order by setting its status to Cancelled."""
    order = order_repo.cancel_order_record(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _build_order_response(order)

def delete_order(order_id: int) -> None:
    """Delete an order by ID."""
    deleted = order_repo.delete_order_record(order_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found")