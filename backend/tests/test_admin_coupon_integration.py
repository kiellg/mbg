"""Integration tests for seeded admin login and admin-only coupon CRUD."""
# pylint: disable=protected-access, duplicate-code

import pytest
from fastapi.testclient import TestClient

from app.data import cart_data, notification_data, order_data
from app.data.users_data import SEEDED_ADMIN_EMAIL, SEEDED_ADMIN_PASSWORD
from app.dependencies import get_current_user
from app.repositories import coupon_repo, restaurant_repo, user_repo
from app.repositories.session_repo import reset_session
from main import app

client = TestClient(app)


def setup_function():
    """Reset shared in-memory state before each test."""
    cart_data._CARTDB.clear()
    cart_data.NEXT_CART_ID = 1
    cart_data.NEXT_ITEM_ID = 1
    notification_data.NOTIFICATIONS.clear()
    order_data._ORDERDB.clear()
    order_data.NEXT_ORDER_ITEM_ID = 1
    coupon_repo.reset_coupons()
    user_repo.reset_users()
    restaurant_repo.reset_restaurants()
    reset_session()
    app.dependency_overrides.clear()


def _login_seeded_admin():
    """Log in using the seeded admin account and return the cookie jar."""
    response = client.post(
        "/auth/login",
        json={
            "email": SEEDED_ADMIN_EMAIL,
            "password": SEEDED_ADMIN_PASSWORD,
        },
    )
    assert response.status_code == 200
    return response.cookies


def _register_and_login_role(role: str):
    """Register and log in a non-admin user for access control tests."""
    email = f"{role}@test.com"
    register_response = client.post(
        "/auth/register",
        json={
            "name": role.title(),
            "email": email,
            "password": "password123",
            "role": role,
        },
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "password123",
        },
    )
    assert login_response.status_code == 200
    return login_response.cookies


def _register_customer_for_checkout() -> dict:
    """Register a customer and override auth for customer-only routes."""
    response = client.post(
        "/auth/register",
        json={
            "name": "Checkout Customer",
            "email": "checkout@test.com",
            "password": "password123",
            "role": "customer",
        },
    )
    assert response.status_code == 200
    user = response.json()
    app.dependency_overrides[get_current_user] = lambda: {"user_id": user["user_id"]}
    profile_response = client.patch(
        "/profile/customer",
        json={"delivery_address": "123 Test St"},
    )
    assert profile_response.status_code == 200
    return user


def _add_item_and_get_cart_id() -> int:
    """Add one item to the seeded restaurant cart and return its id."""
    add_response = client.post(
        "/cart/1/items",
        json={"menu_item_id": 1, "quantity": 1},
    )
    assert add_response.status_code == 201
    cart_response = client.get("/cart/1")
    assert cart_response.status_code == 200
    return cart_response.json()["id"]


def test_admin_coupon_lifecycle_endpoints_work_with_seeded_admin():
    """Seeded admin should be able to create, read, update, deactivate, and delete coupons."""
    admin_cookies = _login_seeded_admin()

    create_response = client.post(
        "/admin/coupons",
        cookies=admin_cookies,
        json={
            "code": "save20",
            "discount_type": "percentage",
            "percent_off": 20,
            "minimum_subtotal_cents": 1500,
        },
    )
    assert create_response.status_code == 201
    assert create_response.json()["code"] == "SAVE20"

    list_response = client.get("/admin/coupons", cookies=admin_cookies)
    assert list_response.status_code == 200
    assert any(coupon["code"] == "SAVE20" for coupon in list_response.json())

    get_response = client.get("/admin/coupons/save20", cookies=admin_cookies)
    assert get_response.status_code == 200
    assert get_response.json()["code"] == "SAVE20"

    update_response = client.patch(
        "/admin/coupons/save20",
        cookies=admin_cookies,
        json={"percent_off": 25, "minimum_subtotal_cents": 2000},
    )
    assert update_response.status_code == 200
    assert update_response.json()["percent_off"] == 25
    assert update_response.json()["minimum_subtotal_cents"] == 2000

    deactivate_response = client.patch(
        "/admin/coupons/save20/deactivate",
        cookies=admin_cookies,
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    delete_response = client.delete("/admin/coupons/save20", cookies=admin_cookies)
    assert delete_response.status_code == 204

    missing_response = client.get("/admin/coupons/save20", cookies=admin_cookies)
    assert missing_response.status_code == 404


@pytest.mark.parametrize("role", ["customer", "manager", "driver"])
def test_non_admin_roles_are_rejected_from_coupon_crud(role):
    """Only admins should be able to access coupon CRUD routes."""
    cookies = _register_and_login_role(role)

    response = client.post(
        "/admin/coupons",
        cookies=cookies,
        json={
            "code": "rolefail",
            "discount_type": "percentage",
            "percent_off": 10,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"


def test_debug_routes_require_admin_access():
    """Sensitive debug routes should no longer be public."""
    assert client.get("/auth/debug/users").status_code == 401
    assert client.get("/auth/debug/sessions").status_code == 401
    assert client.get("/checkout/debug/coupons").status_code == 401

    admin_cookies = _login_seeded_admin()

    assert client.get("/auth/debug/users", cookies=admin_cookies).status_code == 200
    assert client.get("/auth/debug/sessions", cookies=admin_cookies).status_code == 200
    assert client.get("/checkout/debug/coupons", cookies=admin_cookies).status_code == 200


def test_admin_created_coupon_affects_future_checkout():
    """Coupons created by admin should be immediately usable during checkout."""
    admin_cookies = _login_seeded_admin()
    create_response = client.post(
        "/admin/coupons",
        cookies=admin_cookies,
        json={
            "code": "spring20",
            "discount_type": "percentage",
            "percent_off": 20,
        },
    )
    assert create_response.status_code == 201

    _register_customer_for_checkout()
    cart_id = _add_item_and_get_cart_id()

    checkout_response = client.post(
        f"/checkout/{cart_id}",
        json={"delivery_method": "walk", "coupon_code": "spring20"},
    )

    assert checkout_response.status_code == 201
    assert checkout_response.json()["coupon_code"] == "SPRING20"
    assert checkout_response.json()["discount"] == "10.00"
    assert checkout_response.json()["discounted_subtotal"] == "39.99"
    assert checkout_response.json()["tax"] == "4.00"
    assert checkout_response.json()["total"] == "48.99"


def test_admin_deactivated_coupon_blocks_future_checkout():
    """Deactivating a coupon through admin CRUD should block future usage."""
    admin_cookies = _login_seeded_admin()
    create_response = client.post(
        "/admin/coupons",
        cookies=admin_cookies,
        json={
            "code": "temp5",
            "discount_type": "fixed_amount",
            "amount_off_cents": 500,
        },
    )
    assert create_response.status_code == 201

    deactivate_response = client.patch(
        "/admin/coupons/temp5/deactivate",
        cookies=admin_cookies,
    )
    assert deactivate_response.status_code == 200

    _register_customer_for_checkout()
    cart_id = _add_item_and_get_cart_id()

    checkout_response = client.post(
        f"/checkout/{cart_id}",
        json={"delivery_method": "walk", "coupon_code": "temp5"},
    )

    assert checkout_response.status_code == 400
    assert checkout_response.json()["detail"] == "Coupon code is inactive."


def test_old_order_keeps_coupon_snapshot_after_admin_coupon_update():
    """Updating a coupon later should not rewrite the stored order pricing snapshot."""
    admin_cookies = _login_seeded_admin()
    create_response = client.post(
        "/admin/coupons",
        cookies=admin_cookies,
        json={
            "code": "flash20",
            "discount_type": "percentage",
            "percent_off": 20,
        },
    )
    assert create_response.status_code == 201

    _register_customer_for_checkout()
    cart_id = _add_item_and_get_cart_id()
    checkout_response = client.post(
        f"/checkout/{cart_id}",
        json={"delivery_method": "walk", "coupon_code": "flash20"},
    )
    assert checkout_response.status_code == 201
    order = checkout_response.json()
    assert order["discount"] == "10.00"

    update_response = client.patch(
        "/admin/coupons/flash20",
        cookies=admin_cookies,
        json={"percent_off": 50},
    )
    assert update_response.status_code == 200

    repricing_response = client.patch(
        f"/orders/{order['order_id']}",
        json={"delivery_method": "car"},
    )

    assert repricing_response.status_code == 200
    assert repricing_response.json()["coupon_code"] == "FLASH20"
    assert repricing_response.json()["discount"] == "10.00"
    assert repricing_response.json()["discounted_subtotal"] == "39.99"
    assert repricing_response.json()["delivery_fee"] == "10.00"
    assert repricing_response.json()["total"] == "53.99"
