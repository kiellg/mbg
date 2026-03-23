"""Integration tests for payment flow."""
# pylint: disable = protected-access
from fastapi.testclient import TestClient

from backend.app.data import cart_data, order_data, payment_data
from backend.app.dependencies import get_current_user
from backend.app.repositories import user_repo, restaurant_repo
from backend.app.schemas.order import OrderStatus
from backend.app.schemas.payment import PaymentStatus
from backend.main import app

client = TestClient(app)

VALID_CARD = {
    "card_number": "1234567891011121",
    "expiry_date": "12/99",
    "cvv": "123",
    "cardholder_name": "John Doe",
}

DECLINED_CARD = {
    "card_number": "1234567890120000",
    "expiry_date": "12/99",
    "cvv": "123",
    "cardholder_name": "John Doe",
}


def setup_function():
    """Reset all in-memory state before each test."""
    cart_data._CARTDB.clear()
    cart_data.NEXT_CART_ID = 1
    cart_data.NEXT_ITEM_ID = 1
    order_data._ORDERDB.clear()
    order_data.NEXT_ORDER_ITEM_ID = 1
    payment_data._PAYMENTDB.clear()
    payment_data._TOKENDB.clear()
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
    client.patch("/profile/customer", json={"delivery_address": "123 Test St"})
    return user


def _checkout_and_get_order_id() -> str:
    """Add item to cart, checkout, and return order_id."""
    client.post("/cart/1/items", json={"menu_item_id": 1, "quantity": 1})
    cart_id = client.get("/cart/1").json()["id"]
    order_res = client.post(f"/checkout/{cart_id}", json={"delivery_method": "walk"})
    assert order_res.status_code == 201
    return order_res.json()["order_id"]


def test_accepted_payment_moves_order_to_cooking():
    """Accepted payment should move order status from Pending to Cooking."""
    _register_customer()
    order_id = _checkout_and_get_order_id()

    response = client.post(f"/payments/{order_id}", json=VALID_CARD)

    assert response.status_code == 201
    assert response.json()["status"] == PaymentStatus.ACCEPTED.value
    assert order_data._ORDERDB[order_id]["status"] == OrderStatus.COOKING.value


def test_declined_payment_leaves_order_as_pending():
    """Declined payment should not change order status from Pending."""
    _register_customer()
    order_id = _checkout_and_get_order_id()

    response = client.post(f"/payments/{order_id}", json=DECLINED_CARD)

    assert response.status_code == 201
    assert response.json()["status"] == "Declined"
    assert order_data._ORDERDB[order_id]["status"] == "Pending"


def test_receipt_available_after_accepted_payment():
    """Receipt should be retrievable after a successful payment."""
    _register_customer()
    order_id = _checkout_and_get_order_id()
    client.post(f"/payments/{order_id}", json=VALID_CARD)

    response = client.get(f"/payments/{order_id}/receipt")

    assert response.status_code == 200
    assert response.json()["order_id"] == order_id
    assert response.json()["message"] == "Payment accepted. Your order is being prepared."


def test_receipt_not_available_after_declined_payment():
    """Receipt should return 404 after a declined payment."""
    _register_customer()
    order_id = _checkout_and_get_order_id()
    client.post(f"/payments/{order_id}", json=DECLINED_CARD)

    response = client.get(f"/payments/{order_id}/receipt")

    assert response.status_code == 404


def test_cannot_pay_twice_for_same_order():
    """Paying for an already paid Cooking order should return 400."""
    _register_customer()
    order_id = _checkout_and_get_order_id()
    client.post(f"/payments/{order_id}", json=VALID_CARD)

    response = client.post(f"/payments/{order_id}", json=VALID_CARD)

    assert response.status_code == 400


def test_save_payment_method_and_retrieve():
    """Customer should be able to save a card and retrieve it."""
    _register_customer()

    save_res = client.post("/payments/methods", json={
        **VALID_CARD,
        "nickname": "My Visa",
    })
    assert save_res.status_code == 201
    assert save_res.json()["last4"] == "1121"
    assert save_res.json()["nickname"] == "My Visa"

    get_res = client.get("/payments/methods")
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["last4"] == "1121"


def test_pay_with_saved_method_accepts_payment():
    """Customer should be able to pay using a saved payment method."""
    _register_customer()

    save_res = client.post("/payments/methods", json={
        **VALID_CARD,
        "nickname": "My Visa",
    })
    saved_method_id = save_res.json()["saved_method_id"]

    order_id = _checkout_and_get_order_id()
    response = client.post(f"/payments/{order_id}/saved/{saved_method_id}")

    assert response.status_code == 201
    assert response.json()["status"] == "Accepted"
    assert order_data._ORDERDB[order_id]["status"] == "Cooking"


def test_invalid_card_number_returns_400():
    """Payment with invalid card number should return 400."""
    _register_customer()
    order_id = _checkout_and_get_order_id()

    response = client.post(f"/payments/{order_id}", json={
        **VALID_CARD,
        "card_number": "1234",
    })

    assert response.status_code == 400


def test_expired_card_returns_400():
    """Payment with expired card should return 400."""
    _register_customer()
    order_id = _checkout_and_get_order_id()

    response = client.post(f"/payments/{order_id}", json={
        **VALID_CARD,
        "expiry_date": "01/20",
    })

    assert response.status_code == 400
