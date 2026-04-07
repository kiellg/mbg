"""Service layer for order management, handling business logic
and interactions with the order repository."""
from decimal import Decimal
from datetime import datetime
from types import SimpleNamespace
from fastapi import HTTPException
from app.repositories import order_repo, restaurant_repo, user_repo
from app.schemas.order import (
    DeliveryMethod,
    OrderCreate,
    OrderItemCreate,
    OrderResponse,
    OrderItemResponse,
    PendingOrderItemUpdate,
    PendingOrderUpdate,
    OrderUpdate
)
from app.services import notification_service
from app.services.pricing_service import PricingService

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

def _authorize_pending_order_editor(order: dict, user_id: str) -> None:
    """Ensure the current user can edit the pending order."""
    if order["customer_id"] == user_id:
        return

    if user_repo.get_user_role(user_id) != "manager":
        raise HTTPException(status_code=403, detail="Not authorized to modify this order.")

    restaurant = restaurant_repo.get_restaurant_record(order["restaurant_id"])
    if restaurant is None or restaurant.get("owner_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this order.")

def _resolve_pending_order_items(
    restaurant_id: int,
    items: list[PendingOrderItemUpdate],
) -> list[OrderItemCreate]:
    """Resolve pending order item prices from official menu data."""
    resolved_items = []
    unavailable = []

    for item in items:
        menu_item = restaurant_repo.get_menu_item(restaurant_id, item.menu_item_id)
        if menu_item is None:
            raise HTTPException(
                status_code=404,
                detail=f"Menu item {item.menu_item_id} not found.",
            )

        if not menu_item.get("is_available", False):
            unavailable.append(menu_item.get("name", f"item {item.menu_item_id}"))
            continue

        price_cents = menu_item.get("price_cents")
        if price_cents is None or price_cents < 0:
            raise HTTPException(status_code=500, detail="Invalid menu pricing data.")

        resolved_items.append(
            OrderItemCreate(
                quantity=item.quantity,
                item_price=Decimal(price_cents) / Decimal("100"),
            )
        )

    if unavailable:
        raise HTTPException(
            status_code=400,
            detail=f"The following items are not available: {', '.join(unavailable)}",
        )

    return resolved_items

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
        scheduled_time=order.get("scheduled_time"),
        is_scheduled=order.get("is_scheduled", False),
    )
    return response

def create_order(payload: OrderCreate) -> OrderResponse:
    """Create a new order and return the created order details."""
    if payload.scheduled_time:
        if payload.scheduled_time <= datetime.utcnow():
            raise HTTPException(
                status_code=400,
                detail="Scheduled time must be in the future",
            )

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
        scheduled_time=payload.scheduled_time.isoformat() if payload.scheduled_time else None,
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
    _process_scheduled_orders()

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

def update_pending_order(
    order_id: str,
    user_id: str,
    payload: PendingOrderUpdate,
) -> OrderResponse:
    """Update an editable pending order for the owner or restaurant manager."""
    order = order_repo.get_order_record(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    _authorize_pending_order_editor(order, user_id)
    _validate_order_is_pending(order)

    resolved_items = None
    if payload.items is not None:
        resolved_items = _resolve_pending_order_items(order["restaurant_id"], payload.items)

    return update_order(
        order_id,
        OrderUpdate(
            delivery_address=payload.delivery_address,
            delivery_method=payload.delivery_method,
            items=resolved_items,
        ),
    )

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

def _process_scheduled_orders():
    """Activate scheduled orders when their scheduled_time is reached"""
    now = datetime.utcnow()

    for order in order_repo.list_order_records():
        if order.get("is_scheduled") and order.get("scheduled_time"):
            scheduled_time = datetime.fromisoformat(order["scheduled_time"])

            if scheduled_time <= now:
                order_repo.update_order_record(
                    order["order_id"],
                    {
                        "status": "Pending",
                        "is_scheduled": False,
                    },
                )
