"""Integration tests for pricing through checkout and pending-order routes."""
# pylint: disable=protected-access

from fastapi.testclient import TestClient

from backend.app.data import cart_data, notification_data, order_data
from backend.app.dependencies import get_current_user
from backend.app.repositories import restaurant_repo, user_repo
from backend.main import app

client = TestClient(app)


def setup_function():
    """Reset shared in-memory state before each test."""
    cart_data._CARTDB.clear()
    cart_data.NEXT_CART_ID = 1
    cart_data.NEXT_ITEM_ID = 1
    notification_data.NOTIFICATIONS.clear()
    order_data._ORDERDB.clear()
    order_data.NEXT_ORDER_ITEM_ID = 1
    user_repo.reset_users()
    restaurant_repo.reset_restaurants()
    app.dependency_overrides.clear()


def _register_customer() -> dict:
    """Register a customer, store a delivery address, and override auth."""
    res = client.post(
        "/auth/register",
        json={
            "name": "Test Customer",
            "email": "customer@test.com",
            "password": "password123",
            "role": "customer",
        },
    )
    assert res.status_code == 200
    user = res.json()
    app.dependency_overrides[get_current_user] = lambda: {"user_id": user["user_id"]}
    profile_res = client.patch("/profile/customer", json={"delivery_address": "123 Test St"})
    assert profile_res.status_code == 200
    return user


def _add_item_and_get_cart_id(
    *,
    menu_item_id: int = 1,
    quantity: int = 1,
    restaurant_id: int = 1,
) -> int:
    """Add an item to the cart and return the cart id."""
    add_res = client.post(
        f"/cart/{restaurant_id}/items",
        json={"menu_item_id": menu_item_id, "quantity": quantity},
    )
    assert add_res.status_code == 201
    cart_res = client.get(f"/cart/{restaurant_id}")
    assert cart_res.status_code == 200
    return cart_res.json()["id"]


def _checkout_order(
    *,
    menu_item_id: int = 1,
    quantity: int = 1,
    delivery_method: str = "walk",
) -> dict:
    """Create an order through the real checkout route and return the JSON payload."""
    cart_id = _add_item_and_get_cart_id(menu_item_id=menu_item_id, quantity=quantity)
    response = client.post(f"/checkout/{cart_id}", json={"delivery_method": delivery_method})
    assert response.status_code == 201
    return response.json()


def test_checkout_persists_pricing_breakdown_from_real_menu_prices():
    """Checkout should persist totals produced from the seeded restaurant menu price."""
    _register_customer()

    response = _checkout_order(quantity=2)
    stored_order = order_data._ORDERDB[response["order_id"]]

    assert response["items"][0]["item_price"] == "49.99"
    assert response["subtotal"] == "99.98"
    assert response["tax"] == "10.00"
    assert response["delivery_fee"] == "5.00"
    assert response["total"] == "114.98"
    assert stored_order["subtotal"] == "99.98"
    assert stored_order["tax"] == "10.00"
    assert stored_order["delivery_fee"] == "5.00"
    assert stored_order["total"] == "114.98"


def test_pending_order_delivery_method_change_reprices_persisted_total():
    """Changing delivery method through the order route should reprice the stored order."""
    _register_customer()
    order = _checkout_order()

    response = client.patch(
        f"/orders/{order['order_id']}",
        json={"delivery_method": "car"},
    )
    stored_order = order_data._ORDERDB[order["order_id"]]

    assert response.status_code == 200
    assert response.json()["delivery_method"] == "car"
    assert response.json()["subtotal"] == "49.99"
    assert response.json()["tax"] == "5.00"
    assert response.json()["delivery_fee"] == "10.00"
    assert response.json()["total"] == "64.99"
    assert stored_order["delivery_method"] == "car"
    assert stored_order["delivery_fee"] == "10.00"
    assert stored_order["total"] == "64.99"


def test_pending_order_item_replacement_reprices_using_real_menu_item_price():
    """Replacing pending-order items should resolve real menu prices and recalculate totals."""
    _register_customer()
    order = _checkout_order()

    response = client.patch(
        f"/orders/{order['order_id']}",
        json={"items": [{"menu_item_id": 2, "quantity": 3}]},
    )
    stored_order = order_data._ORDERDB[order["order_id"]]

    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 3
    assert response.json()["items"][0]["item_price"] == "9.99"
    assert response.json()["subtotal"] == "29.97"
    assert response.json()["tax"] == "3.00"
    assert response.json()["delivery_fee"] == "5.00"
    assert response.json()["total"] == "37.97"
    assert stored_order["items"][0]["quantity"] == 3
    assert stored_order["items"][0]["item_price"] == "9.99"
    assert stored_order["subtotal"] == "29.97"
    assert stored_order["total"] == "37.97"


def test_pending_order_update_returns_500_for_invalid_menu_pricing_data():
    """Invalid seeded menu pricing should surface through the real pending-order flow."""
    _register_customer()
    order = _checkout_order()

    response = client.patch(
        f"/orders/{order['order_id']}",
        json={"items": [{"menu_item_id": 3, "quantity": 1}]},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Invalid menu pricing data."
