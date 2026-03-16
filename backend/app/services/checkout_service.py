"""Service layer for checkout operations.
Bridges the cart and order systems:
- Reads and validates the cart
- Converts cart item from cents to Decimal for order pricing
- Creates the order via order_service
- Marks the cart as checked out to prevent further modifications"""

from decimal import Decimal
from fastapi import HTTPException
from backend.app.repositories import cart_repo
from backend.app.repositories import user_repo
from backend.app.repositories import restaurant_repo
from backend.app.schemas.order import (
    DeliveryMethod,
    OrderCreate,
    OrderItemCreate,
    OrderResponse,
)
from backend.app.services import order_service

def checkout(cart_id: int,
             customer_id: str,
             delivery_method: DeliveryMethod,
             ) -> OrderResponse:
    """Convert a cart into a new pending order.
    Raises 404 if the cart is not found.
    Raises 403 if the cart does not belong to the customer.
    Raises 400 if the cart is empty or already checked out."""

    cart = cart_repo.get_cart_by_id(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")

    if cart["customer_id"] != customer_id:
        raise HTTPException(status_code=403, detail="Cart does not belong to the customer.")

    if cart.get("checked_out", False):
        raise HTTPException(status_code=400, detail="Cart has already been checked out.")

    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty.")

    customer = user_repo.get_customer_by_user_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found.")

    delivery_address = customer["delivery_address"]
    if not delivery_address:
        raise HTTPException(status_code=400, detail="Customer does not have a delivery address.")

    validated_items = _validate_cart_items(cart)

    items = [
        OrderItemCreate(
            quantity=item["quantity"],
            item_price=Decimal(item["price_cents"]) / Decimal("100")
        )
        for item in validated_items
    ]

    payload = OrderCreate(
        customer_id = customer_id,
        restaurant_id = cart["restaurant_id"],
        delivery_address=delivery_address,
        delivery_method=delivery_method,
        items=items,
    )

    order = order_service.create_order(payload)

    cart_repo.mark_cart_checked_out(cart_id)

    return order

def _validate_cart_items(cart: dict) -> list[dict]:
    """Re-validate cart items against current menu availability and pricing."""
    validated_items = []
    unavailable = []

    for cart_item in cart["items"]:
        menu_item = restaurant_repo.get_menu_item(
            cart["restaurant_id"],
            cart_item["menu_item_id"]
        )
        if menu_item is None or not menu_item.get("is_available", False):
            name = menu_item["name"] if menu_item else f"item {cart_item['menu_item_id']}"
            unavailable.append(name)
            continue

        price_cents = menu_item.get("price_cents")
        if price_cents is None or price_cents < 0:
            raise HTTPException(status_code=500, detail="Invalid menu pricing data.")

        validated_items.append(
            {
                "quantity": cart_item["quantity"],
                "price_cents": price_cents,
            }
        )

    if unavailable:
        raise HTTPException(
            status_code=400,
            detail=f"The following items are no longer available: {', '.join(unavailable)}"
        )

    return validated_items
