"""Integration tests for checkout flow."""
# pylint: disable=protected-access, duplicate-code
from fastapi.testclient import TestClient

from app.data import cart_data, order_data
from app.dependencies import get_current_user
from app.repositories import coupon_repo, user_repo, restaurant_repo
from main import app

client = TestClient(app)


def setup_function():
    """Reset all in-memory state before each test."""
    cart_data._CARTDB.clear()
    cart_data.NEXT_CART_ID = 1
    cart_data.NEXT_ITEM_ID = 1
    order_data._ORDERDB.clear()
    order_data.NEXT_ORDER_ITEM_ID = 1
    coupon_repo.reset_coupons()
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


def test_checkout_applies_percentage_coupon_code():
    """Checkout should apply a valid percentage discount code to the stored totals."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()

    response = client.post(
        f"/checkout/{cart_id}",
        json={"delivery_method": "walk", "coupon_code": "SAVE10"},
    )

    assert response.status_code == 201
    assert response.json()["coupon_code"] == "SAVE10"
    assert response.json()["subtotal"] == "49.99"
    assert response.json()["discount"] == "5.00"
    assert response.json()["discounted_subtotal"] == "44.99"
    assert response.json()["tax"] == "4.50"
    assert response.json()["delivery_fee"] == "5.00"
    assert response.json()["total"] == "54.49"


def test_checkout_applies_fixed_coupon_code():
    """Checkout should apply a valid fixed amount discount code to the stored totals."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()

    response = client.post(
        f"/checkout/{cart_id}",
        json={"delivery_method": "walk", "coupon_code": "TAKE7"},
    )

    assert response.status_code == 201
    assert response.json()["coupon_code"] == "TAKE7"
    assert response.json()["discount"] == "7.00"
    assert response.json()["discounted_subtotal"] == "42.99"
    assert response.json()["tax"] == "4.30"
    assert response.json()["total"] == "52.29"


def test_checkout_rejects_invalid_coupon_code():
    """Checkout should return 400 when a coupon code does not exist."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()

    response = client.post(
        f"/checkout/{cart_id}",
        json={"delivery_method": "walk", "coupon_code": "NOPE"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid coupon code."


def test_checkout_rejects_inactive_coupon_code():
    """Checkout should return 400 when a coupon code is inactive."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()

    response = client.post(
        f"/checkout/{cart_id}",
        json={"delivery_method": "walk", "coupon_code": "INACTIVE10"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Coupon code is inactive."


def test_checkout_rejects_expired_coupon_code():
    """Checkout should return 400 when a coupon code has expired."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()

    response = client.post(
        f"/checkout/{cart_id}",
        json={"delivery_method": "walk", "coupon_code": "EXPIRED5"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Coupon code has expired."


def test_checkout_rejects_coupon_code_below_minimum_subtotal():
    """Checkout should return 400 when the order subtotal is below the coupon minimum."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()

    response = client.post(
        f"/checkout/{cart_id}",
        json={"delivery_method": "walk", "coupon_code": "MIN60"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Order subtotal does not meet the coupon minimum."


def test_checkout_treats_blank_coupon_code_as_absent():
    """Blank coupon codes should behave the same as no coupon code."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()

    response = client.post(
        f"/checkout/{cart_id}",
        json={"delivery_method": "walk", "coupon_code": "   "},
    )

    assert response.status_code == 201
    assert response.json()["coupon_code"] is None
    assert response.json()["discount"] == "0.00"
    assert response.json()["discounted_subtotal"] == "49.99"
    assert response.json()["tax"] == "5.00"
    assert response.json()["total"] == "59.99"


def test_checkout_without_coupon_keeps_existing_totals():
    """Existing checkout totals should stay unchanged when no coupon code is supplied."""
    _register_customer()
    cart_id = _add_item_and_get_cart_id()

    response = client.post(
        f"/checkout/{cart_id}",
        json={"delivery_method": "walk"},
    )

    assert response.status_code == 201
    assert response.json()["coupon_code"] is None
    assert response.json()["subtotal"] == "49.99"
    assert response.json()["discount"] == "0.00"
    assert response.json()["discounted_subtotal"] == "49.99"
    assert response.json()["tax"] == "5.00"
    assert response.json()["delivery_fee"] == "5.00"
    assert response.json()["total"] == "59.99"
