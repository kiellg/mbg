"""Unit tests for cart Pydantic schemas."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from backend.app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse

def test_cart_item_create_valid():
    """Valid input should create a CartItemCreate without errors."""
    item = CartItemCreate(menu_item_id=5, quantity=3)
    assert item.menu_item_id == 5
    assert item.quantity == 3

def test_cart_item_create_rejects_zero_quantity():
    """Zero quantity should raise a ValidationError."""
    with pytest.raises(ValidationError):
        CartItemCreate(menu_item_id=5, quantity=0)

def test_cart_item_create_rejects_negative_quantity():
    """Negative quantity should raise a ValidationError."""
    with pytest.raises(ValidationError):
        CartItemCreate(menu_item_id=5, quantity=-1)

def test_cart_item_create_rejects_missing_menu_item_id():
    """Missing menu_item_id should raise a ValidationError."""
    with pytest.raises(ValidationError):
        CartItemCreate(quantity=2)

def test_cart_item_update_rejects_zero_quantity():
    """Zero quantity in update should raise a ValidationError."""
    with pytest.raises(ValidationError):
        CartItemUpdate(quantity=0)

def test_cart_response_nests_items_correctly():
    """CartResponse should correctly nest a list of CartItemResponse."""
    item = CartItemResponse(
        id=1, cart_id=1, menu_item_id=7, quantity=2,
        item_name="Ribeye Steak", unit_price_cents=4999, subtotal_cents=9998,
    )
    cart = CartResponse(
        id=1, customer_id=42, restaurant_id=3,
        created_at=datetime.utcnow(), items=[item], total_cents=9998,
    )
    assert isinstance(cart.items[0], CartItemResponse)
    assert cart.total_cents == 9998
