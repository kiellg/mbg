"""Integration tests for checkout flow."""
# pylint: disable=protected-access, duplicate-code
from fastapi.testclient import TestClient

from backend.app.data import cart_data, order_data
from backend.app.dependencies import get_current_user
from backend.app.repositories import user_repo, restaurant_repo
from backend.main import app

client = TestClient(app)


def setup_function():
    """Reset all in-memory state before each test."""
    cart_data._CARTDB.clear()
    cart_data.NEXT_CART_ID = 1
    cart_data.NEXT_ITEM_ID = 1
    order_data._ORDERDB.clear()
    order_data.NEXT_ORDER_ITEM_ID = 1
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
    profile_res = client.patch("/profile/customer", json={"delivery_address": "123 Test St"})
    assert profile_res.status_code == 200
    return user


def _add_item_and_get_cart_id() -> int:
    """Add an item to cart and return the cart id."""
    client.post("/cart/1/items", json={"menu_item_id": 1, "quantity": 1})
    cart_res = client.get("/cart/1")
    return cart_res.json()["id"]


def test_full_checkout_flow_creates_pending_order():
    """Full flow: register customer, add item to cart, checkout creates Pending order."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()

    response = client.post(f"/checkout/{cart_id}", json={"delivery_method": "walk"})

    assert response.status_code == 201
    assert response.json()["status"] == "Pending"
    assert response.json()["restaurant_id"] == 1
    assert len(response.json()["items"]) == 1


def test_checkout_marks_cart_as_checked_out():
    """After checkout the cart should be marked as checked out."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()

    client.post(f"/checkout/{cart_id}", json={"delivery_method": "walk"})

    cart = cart_data._CARTDB.get(cart_id)
    assert cart["checked_out"] is True


def test_checkout_fails_if_cart_is_empty():
    """Checkout should return 400 when cart has no items."""
    _register_customer()
    client.post("/cart/1/items", json={"menu_item_id": 1, "quantity": 1})
    cart_res = client.get("/cart/1")
    cart_id = cart_res.json()["id"]
    item_id = cart_res.json()["items"][0]["id"]
    client.delete(f"/cart/1/items/{item_id}")

    response = client.post(f"/checkout/{cart_id}", json={"delivery_method": "walk"})

    assert response.status_code == 400


def test_checkout_fails_if_already_checked_out():
    """Checkout should return 400 when cart has already been checked out."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()
    client.post(f"/checkout/{cart_id}", json={"delivery_method": "walk"})

    response = client.post(f"/checkout/{cart_id}", json={"delivery_method": "walk"})

    assert response.status_code == 400


def test_checkout_uses_official_menu_price():
    """Order items should use the official menu price."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()

    response = client.post(f"/checkout/{cart_id}", json={"delivery_method": "walk"})

    assert response.status_code == 201
    item_price = float(response.json()["items"][0]["item_price"])
    assert item_price == 49.99


def test_checkout_delivery_method_stored_on_order():
    """The delivery method chosen at checkout should be reflected on the order."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()

    response = client.post(f"/checkout/{cart_id}", json={"delivery_method": "car"})

    assert response.status_code == 201
    assert response.json()["delivery_method"] == "car"
