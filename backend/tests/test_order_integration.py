"""Integration tests for pending-order update flow."""
# pylint: disable=protected-access, duplicate-code

from fastapi.testclient import TestClient

from backend.app.data import cart_data, notification_data, order_data, payment_data
from backend.app.dependencies import get_current_user
from backend.app.repositories import restaurant_repo, user_repo
from backend.app.schemas.payment import PaymentStatus
from backend.main import app

client = TestClient(app)

VALID_CARD = {
    "card_number": "1234567891011121",
    "expiry_date": "12/99",
    "cvv": "123",
    "cardholder_name": "John Doe",
}


def setup_function():
    """Reset shared in-memory state before each test."""
    cart_data._CARTDB.clear()
    cart_data.NEXT_CART_ID = 1
    cart_data.NEXT_ITEM_ID = 1
    notification_data.NOTIFICATIONS.clear()
    order_data._ORDERDB.clear()
    order_data.NEXT_ORDER_ITEM_ID = 1
    payment_data._PAYMENTDB.clear()
    payment_data._TOKENDB.clear()
    user_repo.reset_users()
    restaurant_repo.reset_restaurants()
    app.dependency_overrides.clear()


def _set_current_user(user_id: str) -> None:
    """Override auth to the provided user id."""
    app.dependency_overrides[get_current_user] = lambda: {"user_id": user_id}


def _register_customer(*, email: str, name: str, delivery_address: str = "123 Test St") -> dict:
    """Register a customer, store a delivery address, and override auth."""
    res = client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": "password123",
            "role": "customer",
        },
    )
    assert res.status_code == 200
    user = res.json()
    _set_current_user(user["user_id"])
    profile_res = client.patch("/profile/customer", json={"delivery_address": delivery_address})
    assert profile_res.status_code == 200
    return user


def _create_manager(*, name: str, email: str) -> dict:
    """Create a manager user directly in the in-memory repo."""
    user = user_repo.create_user(name, email, "pw123")
    user_repo.create_manager(user["user_id"])
    return user


def _add_item_and_get_cart_id() -> int:
    """Add a seeded menu item to the cart and return the cart id."""
    add_res = client.post("/cart/1/items", json={"menu_item_id": 1, "quantity": 1})
    assert add_res.status_code == 201
    cart_res = client.get("/cart/1")
    assert cart_res.status_code == 200
    return cart_res.json()["id"]


def _checkout_and_get_order() -> dict:
    """Create an order through the real checkout route and return the JSON payload."""
    cart_id = _add_item_and_get_cart_id()
    order_res = client.post(f"/checkout/{cart_id}", json={"delivery_method": "walk"})
    assert order_res.status_code == 201
    return order_res.json()


def _mark_restaurant_owned_by(user_id: str, restaurant_id: int = 1) -> None:
    """Assign the seeded restaurant owner to the provided manager user."""
    restaurant = restaurant_repo.get_restaurant_record(restaurant_id)
    assert restaurant is not None
    restaurant["owner_id"] = user_id


def _pay_order(order_id: str) -> None:
    """Pay for an order through the real payment route."""
    payment_res = client.post(f"/payments/{order_id}", json=VALID_CARD)
    assert payment_res.status_code == 201
    assert payment_res.json()["status"] == PaymentStatus.ACCEPTED.value


def test_customer_can_update_own_pending_order_delivery_address():
    """Customers should be able to update their own pending order address."""
    _register_customer(email="customer1@test.com", name="Customer One")
    order = _checkout_and_get_order()

    response = client.patch(
        f"/orders/{order['order_id']}",
        json={"delivery_address": "456 Updated Ave"},
    )

    assert response.status_code == 200
    assert response.json()["delivery_address"] == "456 Updated Ave"
    assert order_data._ORDERDB[order["order_id"]]["delivery_address"] == "456 Updated Ave"


def test_other_customer_cannot_update_pending_order():
    """A different customer should not be able to edit someone else's order."""
    owner = _register_customer(email="customer1@test.com", name="Customer One")
    order = _checkout_and_get_order()
    _register_customer(email="customer2@test.com", name="Customer Two")

    response = client.patch(
        f"/orders/{order['order_id']}",
        json={"delivery_address": "456 Updated Ave"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to modify this order."
    assert order_data._ORDERDB[order["order_id"]]["customer_id"] == owner["user_id"]
    assert order_data._ORDERDB[order["order_id"]]["delivery_address"] == "123 Test St"


def test_manager_owner_can_update_pending_order():
    """A manager who owns the restaurant should be able to edit the order."""
    _register_customer(email="customer1@test.com", name="Customer One")
    order = _checkout_and_get_order()
    manager = _create_manager(name="Manager One", email="manager1@test.com")
    _mark_restaurant_owned_by(manager["user_id"])
    _set_current_user(manager["user_id"])

    response = client.patch(
        f"/orders/{order['order_id']}",
        json={"delivery_address": "789 Manager Update Rd"},
    )

    assert response.status_code == 200
    assert response.json()["delivery_address"] == "789 Manager Update Rd"
    assert order_data._ORDERDB[order["order_id"]]["delivery_address"] == "789 Manager Update Rd"


def test_non_owner_manager_cannot_update_pending_order():
    """A manager who does not own the restaurant should be rejected."""
    _register_customer(email="customer1@test.com", name="Customer One")
    order = _checkout_and_get_order()
    manager = _create_manager(name="Manager Two", email="manager2@test.com")
    _set_current_user(manager["user_id"])

    response = client.patch(
        f"/orders/{order['order_id']}",
        json={"delivery_address": "789 Manager Update Rd"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to modify this order."
    assert order_data._ORDERDB[order["order_id"]]["delivery_address"] == "123 Test St"


def test_non_pending_order_cannot_be_edited():
    """Orders should become non-editable after a successful payment moves them to Cooking."""
    _register_customer(email="customer1@test.com", name="Customer One")
    order = _checkout_and_get_order()
    _pay_order(order["order_id"])

    response = client.patch(
        f"/orders/{order['order_id']}",
        json={"delivery_address": "456 Updated Ave"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only pending orders can be modified or cancelled."
    assert order_data._ORDERDB[order["order_id"]]["status"] == "Cooking"
    assert order_data._ORDERDB[order["order_id"]]["delivery_address"] == "123 Test St"
