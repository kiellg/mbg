#pylint: disable=unused-argument, unused-import
"""Unit tests for the cart router endpoints."""

from unittest.mock import patch
from datetime import datetime, timezone
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi import HTTPException

from backend.app.routers.carts import router
from backend.app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse

app = FastAPI()
app.include_router(router)

client = TestClient(app)

_SVC = "backend.app.routers.carts.cart_service"

AUTH_HEADER = {"fake-user-id": "7"}

MOCK_CART_ITEM_RESPONSE = CartItemResponse(
    id=1,
    cart_id=1,
    menu_item_id=1,
    quantity=2,
    item_name="Ribeye Steak",
    unit_price_cents=4999,
    subtotal_cents=9998,
)

MOCK_CART_RESPONSE = CartResponse(
    id=1,
    customer_id=7,
    restaurant_id=1,
    created_at=datetime.now(timezone.utc).isoformat(),
    items=[MOCK_CART_ITEM_RESPONSE],
    total_cents=9998
)

# for get cart
@patch(f"{_SVC}.get_cart", return_value=MOCK_CART_RESPONSE)
def test_get_cart_returns_200(mock_get_cart):
    """Test that GET /cart/{restaurant_id} returns 200 with valid cart data."""
    response = client.get("/cart/1", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["customer_id"] == 7
    mock_get_cart.assert_called_once_with(customer_id=7, restaurant_id=1)

@patch(f"{_SVC}.get_cart",
       side_effect=HTTPException(status_code=404, detail="Cart not found"))
def test_get_cart_returns_404_when_cart_not_found(mock_get_cart):
    """Test that GET /cart/{restaurant_id} returns 404 when cart is not found."""
    response = client.get("/cart/1", headers=AUTH_HEADER)
    assert response.status_code == 404

def test_get_cart_returns_422_when_no_auth_header():
    """Test that GET /cart/{restaurant_id} returns 422 when auth header is missing."""
    response = client.get("/cart/1")
    assert response.status_code == 422

# for add item to cart
@patch(f"{_SVC}.add_item", return_value=MOCK_CART_RESPONSE)
def test_add_item_returns_201(mock_add_item):
    """Test that POST /cart/{restaurant_id}/items returns 201 with valid data."""
    payload = {"menu_item_id": 1, "quantity": 2}
    response = client.post("/cart/1/items", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 201
    assert response.json()["total_cents"] == 9998
    mock_add_item.assert_called_once()

@patch(f"{_SVC}.add_item",
       side_effect=HTTPException(status_code=400, detail="Menu item not available"))
def test_add_item_returns_400_when_menu_item_not_available(mock_add_item):
    """Test that POST /cart/{restaurant_id}/items 
    returns 400 when menu item is not available."""
    payload = {"menu_item_id": 8, "quantity": 1}
    response = client.post("/cart/1/items", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 400

@patch(f"{_SVC}.add_item",
       side_effect=HTTPException(status_code=404, detail="Item not found"))
def test_add_item_returns_404_when_item_not_found(mock_add_item):
    """Test that POST /cart/{restaurant_id}/items 
    returns 404 when item is not found."""
    payload = {"menu_item_id": 999, "quantity": 1}
    response = client.post("/cart/1/items", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 404

#for update cart item
@patch(f"{_SVC}.update_item", return_value=MOCK_CART_RESPONSE)
def test_update_cart_item_returns_200(mock_update):
    """Test that PUT /cart/{restaurant_id}/items/{item_id} 
    returns 200 with valid data."""
    payload = {"quantity": 3}
    response = client.put("/cart/1/items/1", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 200
    mock_update.assert_called_once_with(
        customer_id=7,
        restaurant_id=1,
        item_id=1,
        payload=CartItemUpdate(quantity=3),
    )

@patch(f"{_SVC}.update_item",
       side_effect=HTTPException(status_code=404, detail="Cart not found"))
def test_update_cart_item_returns_404_when_cart_not_found(mock_update):
    """Test that PUT /cart/{restaurant_id}/items/{item_id} 
    returns 404 when cart is not found."""
    payload = {"quantity": 3}
    response = client.put("/cart/1/items/1", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 404

@patch(f"{_SVC}.update_item",
       side_effect=HTTPException(status_code=404, detail="Item not found"))
def test_update_cart_item_returns_404_when_item_not_found(mock_update):
    """Test that PUT /cart/{restaurant_id}/items/{item_id} 
    returns 404 when item is not found."""
    payload = {"quantity": 3}
    response = client.put("/cart/1/items/999", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 404

# for remove cart item
@patch(f"{_SVC}.remove_item", return_value=None)
def test_remove_cart_item_returns_204(mock_remove):
    """Test that DELETE /cart/{restaurant_id}/items/{item_id} 
    returns 204 with valid data."""
    response = client.delete("/cart/1/items/1", headers=AUTH_HEADER)
    assert response.status_code == 204
    mock_remove.assert_called_once_with(
        customer_id=7,
        restaurant_id=1,
        item_id=1,
    )

@patch(f"{_SVC}.remove_item",
       side_effect=HTTPException(status_code=404, detail="Cart not found"))
def test_remove_cart_item_returns_404_when_cart_not_found(mock_remove):
    """Test that DELETE /cart/{restaurant_id}/items/{item_id} 
    returns 404 when cart is not found."""
    response = client.delete("/cart/1/items/1", headers=AUTH_HEADER)
    assert response.status_code == 404

@patch(f"{_SVC}.remove_item",
       side_effect=HTTPException(status_code=404, detail="Item not found"))
def test_remove_cart_item_returns_404_when_item_not_found(mock_remove):
    """Test that DELETE /cart/{restaurant_id}/items/{item_id} 
    returns 404 when item is not found."""
    response = client.delete("/cart/1/items/999", headers=AUTH_HEADER)
    assert response.status_code == 404
