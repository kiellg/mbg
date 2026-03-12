"""Handles all read and write data. No business logic."""

#pylint: disable=protected-access
from typing import Any, Dict, List, Optional
from datetime import datetime
from backend.app.data import cart_data

def get_cart_by_customer_and_restaurant(customer_id: str,
                                        restaurant_id: int) -> Optional[Dict[str, Any]]:
    """Search for a cart matching the given customer and restaurant IDs."""
    for cart in cart_data._CARTDB.values():
        if cart["customer_id"] == customer_id and cart["restaurant_id"] == restaurant_id:
            return cart
    return None

def get_cart_by_id(cart_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a cart by its unique ID."""
    return cart_data._CARTDB.get(cart_id)

def create_cart(customer_id: str, restaurant_id: int) -> Dict[str, Any]:
    """Create a new cart for the specified customer and restaurant."""
    cart_id = cart_data.NEXT_CART_ID
    cart_data.NEXT_CART_ID += 1
    new_cart = {
        "id": cart_id,
        "customer_id": customer_id,
        "restaurant_id": restaurant_id,
        "created_at": datetime.utcnow().isoformat(),
        "items": []
    }
    cart_data._CARTDB[cart_id] = new_cart
    return new_cart

def add_item_to_cart(cart_id: int, menu_item_id: int, quantity: int) -> Optional[Dict[str, Any]]:
    """Add a new item to the specified cart."""
    cart = get_cart_by_id(cart_id)
    if not cart:
        return None

    item_id = cart_data.NEXT_ITEM_ID
    cart_data.NEXT_ITEM_ID += 1

    new_item = {
        "id": item_id,
        "cart_id": cart_id,
        "menu_item_id": menu_item_id,
        "quantity": quantity
    }
    cart["items"].append(new_item)
    return new_item

def update_item_quantity(cart_id: int, item_id: int, quantity: int) -> Optional[Dict[str, Any]]:
    """Update the quantity of an existing item in the cart."""
    cart = get_cart_by_id(cart_id)
    if not cart:
        return None

    for item in cart["items"]:
        if item["id"] == item_id:
            item["quantity"] = quantity
            return item
    return None

def remove_item_from_cart(cart_id: int, item_id: int) -> bool:
    """Remove an item from the cart by its ID."""
    cart = get_cart_by_id(cart_id)
    if not cart:
        return False

    for i, item in enumerate(cart["items"]):
        if item["id"] == item_id:
            del cart["items"][i]
            return True
    return False

def get_cart_items(cart_id: int) -> Optional[List[Dict[str, Any]]]:
    """Retrieve all items in the specified cart."""
    cart = get_cart_by_id(cart_id)
    if not cart:
        return None
    return cart["items"]
