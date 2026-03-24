"""Integration tests for cart flow."""
# pylint: disable=protected-access, duplicate-code
from fastapi.testclient import TestClient

from backend.app.data import cart_data
from backend.app.dependencies import get_current_user
from backend.app.repositories import user_repo, restaurant_repo
from backend.main import app

client = TestClient(app)


def setup_function():
    """Reset all in-memory state before each test."""
    cart_data._CARTDB.clear()
    cart_data.NEXT_CART_ID = 1
    cart_data.NEXT_ITEM_ID = 1
    user_repo.reset_users()
    restaurant_repo.reset_restaurants()
    app.dependency_overrides.clear()


def _register_customer() -> dict:
    """Register a customer and override auth. Returns user dict."""
    res = client.post("/auth/register", json={
        "name": "Test Customer",
        "email": "customer@test.com",
        "password": "password123",
        "role": "customer",
    })
    assert res.status_code == 200
    user = res.json()
    app.dependency_overrides[get_current_user] = lambda: {"user_id": user["user_id"]}
    client.post("/profile/customer", json={"delivery_address": "123 Test St"})
    return user

def test_add_item_to_cart_creates_cart_and_returns_response():
    """Adding an item to a cart should create a cart and return correct data."""
    _register_customer()

    response = client.post("/cart/1/items", json={"menu_item_id": 1, "quantity": 2})

    assert response.status_code == 201
    assert response.json()["restaurant_id"] == 1
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["quantity"] == 2


def test_add_multiple_items_accumulates_in_cart():
    """Adding multiple items should accumulate them in the same cart."""
    _register_customer()

    client.post("/cart/1/items", json={"menu_item_id": 1, "quantity": 1})
    response = client.post("/cart/1/items", json={"menu_item_id": 1, "quantity": 2})

    assert response.status_code == 201
    assert response.json()["cart_subtotal_cents"] > 0
    assert response.json()["items"][0]["quantity"] == 3


def test_get_cart_returns_correct_cart():
    """Getting a cart should return the correct cart for the customer."""
    _register_customer()
    client.post("/cart/1/items", json={"menu_item_id": 1, "quantity": 1})

    response = client.get("/cart/1")

    assert response.status_code == 200
    assert response.json()["restaurant_id"] == 1
    assert len(response.json()["items"]) == 1


def test_update_cart_item_changes_quantity():
    """Updating a cart item should change its quantity."""
    _register_customer()
    client.post("/cart/1/items", json={"menu_item_id": 1, "quantity": 1})
    cart = client.get("/cart/1").json()
    item_id = cart["items"][0]["id"]

    response = client.put(f"/cart/1/items/{item_id}", json={"quantity": 3})

    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 3


def test_remove_cart_item_empties_cart():
    """Removing the only item should result in an empty cart."""
    _register_customer()
    client.post("/cart/1/items", json={"menu_item_id": 1, "quantity": 1})
    cart = client.get("/cart/1").json()
    item_id = cart["items"][0]["id"]

    response = client.delete(f"/cart/1/items/{item_id}")

    assert response.status_code == 204
    updated_cart = client.get("/cart/1").json()
    assert updated_cart["items"] == []


def test_cart_subtotal_reflects_item_prices():
    """Cart subtotal should correctly reflect item prices from the menu."""
    _register_customer()

    client.post("/cart/1/items", json={"menu_item_id": 1, "quantity": 1})
    response = client.get("/cart/1")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["cart_subtotal_cents"] > 0
    assert response.json()["display_cart_subtotal"] != ""


def test_add_unavailable_item_returns_400():
    """Adding an unavailable menu item should return 400."""
    _register_customer()

    response = client.post("/cart/1/items", json={"menu_item_id": 5, "quantity": 1})

    assert response.status_code == 400
