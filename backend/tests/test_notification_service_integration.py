"""Integration tests for notification flows and notification routes."""
# pylint: disable=protected-access, duplicate-code

from fastapi.testclient import TestClient

from app.data import cart_data, notification_data, order_data, payment_data
from app.dependencies import get_current_user
from app.repositories import restaurant_repo, user_repo
from app.schemas.payment import PaymentStatus
from app.services import delivery_service
from main import app

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
    """Override the current user dependency for the integration flow."""
    app.dependency_overrides[get_current_user] = lambda: {"user_id": user_id}


def _register_customer() -> dict:
    """Register a customer, store an address, and override auth."""
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
    _set_current_user(user["user_id"])
    profile_res = client.patch("/profile/customer", json={"delivery_address": "123 Test St"})
    assert profile_res.status_code == 200
    return user


def _create_manager() -> dict:
    """Create a manager user for visibility checks."""
    manager = user_repo.create_user("mgr", "manager@test.com", "pw123")
    user_repo.create_manager(manager["user_id"])
    return manager


def _create_driver() -> dict:
    """Create a driver user for notification visibility checks."""
    driver = user_repo.create_user("drv", "driver@test.com", "pw123")
    user_repo.create_driver(driver["user_id"], delivery_method="walk")
    return driver


def _checkout_and_get_order_id() -> str:
    """Add an item to cart, checkout, and return the order id."""
    add_res = client.post("/cart/1/items", json={"menu_item_id": 1, "quantity": 1})
    assert add_res.status_code == 201
    cart_id = client.get("/cart/1").json()["id"]
    order_res = client.post(f"/checkout/{cart_id}", json={"delivery_method": "walk"})
    assert order_res.status_code == 201
    return order_res.json()["order_id"]


def _accept_payment(order_id: str):
    """Pay for an order so it moves to Cooking and creates a notification."""
    response = client.post(f"/payments/{order_id}", json=VALID_CARD)
    assert response.status_code == 201
    assert response.json()["status"] == PaymentStatus.ACCEPTED.value


def test_checkout_creates_notification_visible_through_notifications_route():
    """Checkout should create an order-placed notification visible to the customer."""
    _register_customer()
    order_id = _checkout_and_get_order_id()

    response = client.get("/notifications")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["order_id"] == order_id
    assert response.json()[0]["message"] == "Order placed."
    assert response.json()[0]["is_read"] is False


def test_accepted_payment_adds_status_change_notification_newest_first():
    """Accepted payment should add a newer status-change notification for the same order."""
    _register_customer()
    order_id = _checkout_and_get_order_id()

    payment_response = client.post(f"/payments/{order_id}", json=VALID_CARD)
    notifications_response = client.get("/notifications")

    assert payment_response.status_code == 201
    assert payment_response.json()["status"] == PaymentStatus.ACCEPTED.value
    assert notifications_response.status_code == 200
    assert [item["message"] for item in notifications_response.json()] == [
        "Order status changed to Cooking.",
        "Order placed.",
    ]
    assert [item["order_id"] for item in notifications_response.json()] == [
        order_id,
        order_id,
    ]


def test_mark_notification_as_read_updates_customer_view():
    """Marking a notification as read should update the current customer's view."""
    _register_customer()
    _checkout_and_get_order_id()

    notifications_response = client.get("/notifications")
    notification_id = notifications_response.json()[0]["notification_id"]

    read_response = client.patch(f"/notifications/{notification_id}/read")
    updated_notifications_response = client.get("/notifications")

    assert read_response.status_code == 200
    assert read_response.json()["is_read"] is True
    assert updated_notifications_response.status_code == 200
    assert updated_notifications_response.json()[0]["is_read"] is True


def test_notification_read_state_is_user_specific_for_customer_and_manager():
    """Customer reads should not mark a shared Cooking notification as read for a manager."""
    customer = _register_customer()
    manager = _create_manager()
    restaurant_repo.get_restaurant_record(1)["owner_id"] = manager["user_id"]

    order_id = _checkout_and_get_order_id()
    _accept_payment(order_id)
    customer_notifications = client.get("/notifications")
    notification_id = customer_notifications.json()[0]["notification_id"]

    read_response = client.patch(f"/notifications/{notification_id}/read")
    assert read_response.status_code == 200

    customer_notifications = client.get("/notifications")
    assert customer_notifications.status_code == 200
    assert customer_notifications.json()[0]["order_id"] == order_id
    assert customer_notifications.json()[0]["is_read"] is True

    _set_current_user(manager["user_id"])
    manager_notifications = client.get("/notifications")

    assert manager_notifications.status_code == 200
    assert len(manager_notifications.json()) == 1
    assert manager_notifications.json()[0]["order_id"] == order_id
    assert manager_notifications.json()[0]["is_read"] is False
    assert manager_notifications.json()[0]["message"] == "Order status changed to Cooking."
    assert customer["user_id"] != manager["user_id"]


def test_driver_assignment_notification_is_visible_only_to_assigned_driver():
    """Driver assignment should not leak driver-only notifications to other roles."""
    customer = _register_customer()
    manager = _create_manager()
    driver = _create_driver()
    restaurant_repo.get_restaurant_record(1)["owner_id"] = manager["user_id"]

    order_id = _checkout_and_get_order_id()
    _accept_payment(order_id)
    delivery_service.assign_driver_to_order(
        order_id,
        driver["user_id"],
        manager["user_id"],
        "walk",
    )

    _set_current_user(customer["user_id"])
    customer_notifications = client.get("/notifications")
    assert customer_notifications.status_code == 200
    assert [item["message"] for item in customer_notifications.json()] == [
        "Order status changed to Cooking.",
        "Order placed.",
    ]

    _set_current_user(manager["user_id"])
    manager_notifications = client.get("/notifications")
    assert manager_notifications.status_code == 200
    assert [item["message"] for item in manager_notifications.json()] == [
        "Order status changed to Cooking.",
    ]

    _set_current_user(driver["user_id"])
    driver_notifications = client.get("/notifications")
    assert driver_notifications.status_code == 200
    assert [item["message"] for item in driver_notifications.json()] == [
        "You have been assigned a delivery.",
    ]
