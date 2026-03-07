"""Business logic for cart operations."""

from fastapi import HTTPException

from backend.app.data.restaurants_data import _DB as RESTAURANT_DB
from backend.app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse
import backend.app.repositories.cart_repo as cart_repo

def _get_menu_item(restaurant_id: int, menu_item_id: int) -> dict:
    """Fetch a menu from the restaurant database. Raises HTTPException if not found."""
    restaurant = RESTAURANT_DB.get(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail=f"Restaurant {restaurant_id} not found")

    for item in restaurant.get("menu", []):
        if item["id"] == menu_item_id:
            return item

    raise HTTPException(
        status_code=404, 
        detail=f"Menu item {menu_item_id} not found in restaurant {restaurant_id}")

def _build_cart_response(cart: dict) -> CartResponse:
    """Convert a cart dictionary into a CartResponse schema."""
    restaurant_id = cart["restaurant_id"]
    item_responses = []

    for cart_item in cart["items"]:
        menu_item = _get_menu_item(restaurant_id, cart_item["menu_item_id"])
        subtotal = menu_item["price_cents"] * cart_item["quantity"]
        item_responses.append(CartItemResponse(
            id=cart_item["id"],
            cart_id=cart_item["cart_id"],
            menu_item_id=cart_item["menu_item_id"],
            quantity=cart_item["quantity"],
            item_name=menu_item["name"],
            unit_price_cents=menu_item["price_cents"],
            subtotal_cents=subtotal,
        ))

    total = sum(item.subtotal_cents for item in item_responses)

    return CartResponse(
        id=cart["id"],
        customer_id=cart["customer_id"],
        restaurant_id=cart["restaurant_id"],
        created_at=cart["created_at"],
        items=item_responses,
        total_cents=total
    )

def add_item(customer_id: int, restaurant_id: int, payload: CartItemCreate) -> CartItemResponse:
    """Add an item to the customer's cart, creating a cart if necessary."""
    menu_item = _get_menu_item(restaurant_id, payload.menu_item_id)
    if not menu_item.get("is_available", False):
        raise HTTPException(status_code=400, detail=f"Menu item {payload.menu_item_id} is not available")

    cart = cart_repo.get_cart_by_customer_and_restaurant(customer_id, restaurant_id)
    if cart is None:
        cart = cart_repo.create_cart(customer_id, restaurant_id)

    cart_repo.add_item_to_cart(cart["id"], payload.menu_item_id, payload.quantity)
    
    return _build_cart_response(cart)

def update_item(customer_id: int, cart_id: int, item_id: int, payload: CartItemUpdate) -> CartResponse:
    """Update the quantity of an item in the customer's cart."""
    
    cart = cart_repo.get_cart_by_id(cart_id)
    if cart is None or cart["customer_id"] != customer_id:
        raise HTTPException(status_code=404, detail=f"Cart {cart_id} not found")

    updated_item = cart_repo.update_cart_item(cart_id, item_id, payload.quantity)
    if updated_item is None:
        raise HTTPException(status_code=404, detail=f"Cart item {item_id} is not found in cart {cart_id}")

    return _build_cart_response(cart)

def remove_item(customer_id: int, cart_id: int, item_id: int) -> None:
    """Remove an item from the customer's cart."""
    cart = cart_repo.get_cart_by_id(cart_id)
    if cart is None or cart["customer_id"] != customer_id:
        raise HTTPException(status_code=404, detail=f"Cart {cart_id} not found")

    removed = cart_repo.remove_item_from_cart(cart_id, item_id)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Cart item {item_id} is not found in cart {cart_id}")
    
def get_cart(customer_id: int, restaurant_id: int) -> CartResponse:
    """Retrieve the customer's cart for a specific restaurant."""
    cart = cart_repo.get_cart_by_customer_and_restaurant(customer_id, restaurant_id)
    if cart is None:
        raise HTTPException(status_code=404, detail=f"No cart found for customer {customer_id} at restaurant {restaurant_id}")
    
    return _build_cart_response(cart)
