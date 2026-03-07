"""Cart router: defines all API endpoints for cart operations."""

from fastapi import APIRouter, Depends, status

from backend.app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from backend.app.services import cart_service as cart_service
from backend.app.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/{restaurant_id}", response_model=CartResponse)
def get_cart(
    restaurant_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Get the current user's cart for a specific restaurant."""
    return cart_service.get_cart(
        customer_id=current_user["id"],
        restaurant_id=restaurant_id,
    )


@router.post("/{restaurant_id}/items", response_model=CartResponse,
             status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
    restaurant_id: int,
    payload: CartItemCreate,
    current_user: dict = Depends(get_current_user),
):
    """Add a menu item to the cart for a specific restaurant."""
    return cart_service.add_item(
        customer_id=current_user["id"],
        restaurant_id=restaurant_id,
        payload=payload,
    )


@router.put("/{restaurant_id}/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    restaurant_id: int,
    item_id: int,
    payload: CartItemUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update the quantity of an existing cart item."""
    return cart_service.update_item(
        customer_id=current_user["id"],
        restaurant_id=restaurant_id,
        item_id=item_id,
        payload=payload,
    )


@router.delete(
    "/{restaurant_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_cart_item(
    restaurant_id: int,
    item_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Remove an item from the cart."""
    cart_service.remove_item(
        customer_id=current_user["id"],
        restaurant_id=restaurant_id,
        item_id=item_id,
    )
