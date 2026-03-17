"""Unit tests for notification_service.py."""
# pylint: disable=protected-access

from backend.app.data import order_data
from backend.app.data.notification_data import NOTIFICATIONS
from backend.app.repositories import order_repo, restaurant_repo, user_repo
from backend.app.repositories.notification_repo import create_notification
from backend.app.services import notification_service


def setup_function():
    """Reset notification state before each test."""
    NOTIFICATIONS.clear()
    order_data._ORDERDB.clear()
    order_data.NEXT_ORDER_ITEM_ID = 1
    user_repo.reset_users()
    restaurant_repo.reset_restaurants()


def _create_order(customer_id: str, restaurant_id: int) -> dict:
    """Create a minimal stored order for notification tests."""
    return order_repo.create_order_record(
        customer_id=customer_id,
        restaurant_id=restaurant_id,
        delivery_address="123 Test St",
        items=[{"quantity": 1, "item_price": "12.50"}],
    )


def test_create_order_placed_notification_stores_minimal_record():
    """Order placement notifications should store message, timestamp, and order_id."""
    record = notification_service.create_order_placed_notification("abc1234")

    assert record["message"] == "Order placed."
    assert record["order_id"] == "abc1234"
    assert "timestamp" in record
    assert NOTIFICATIONS == [record]


def test_create_order_status_changed_notification_stores_minimal_record():
    """Status change notifications should store message, timestamp, and order_id."""
    record = notification_service.create_order_status_changed_notification(
        "abc1234",
        "Cooking",
    )

    assert record["message"] == "Order status changed to Cooking."
    assert record["order_id"] == "abc1234"
    assert "timestamp" in record
    assert NOTIFICATIONS == [record]


def test_list_notifications_for_customer_returns_only_own_newest_first():
    """Customers should only see their own notifications in newest-first order."""
    customer = user_repo.create_user("cust", "cust@email.com", "pw123")
    user_repo.create_customer(customer["user_id"])

    other_customer = user_repo.create_user("other", "other@email.com", "pw123")
    user_repo.create_customer(other_customer["user_id"])

    first_order = _create_order(customer["user_id"], 1)
    create_notification("First", first_order["order_id"])

    other_order = _create_order(other_customer["user_id"], 1)
    create_notification("Other", other_order["order_id"])

    newest_order = _create_order(customer["user_id"], 2)
    create_notification("Newest", newest_order["order_id"])

    result = notification_service.list_notifications_for_user(customer["user_id"])

    assert [item.order_id for item in result] == [
        newest_order["order_id"],
        first_order["order_id"],
    ]


def test_list_notifications_for_manager_returns_only_owned_restaurant_orders():
    """Managers should only see notifications for restaurants they own."""
    manager = user_repo.create_user("mgr", "mgr@email.com", "pw123")
    user_repo.create_manager(manager["user_id"])

    other_manager = user_repo.create_user("other-mgr", "othermgr@email.com", "pw123")
    user_repo.create_manager(other_manager["user_id"])

    restaurant_repo.get_restaurant_record(1)["owner_id"] = manager["user_id"]
    restaurant_repo.get_restaurant_record(2)["owner_id"] = other_manager["user_id"]

    first_order = _create_order("customer-1", 1)
    create_notification("First", first_order["order_id"])

    other_order = _create_order("customer-2", 2)
    create_notification("Other", other_order["order_id"])

    newest_order = _create_order("customer-3", 1)
    create_notification("Newest", newest_order["order_id"])

    result = notification_service.list_notifications_for_user(manager["user_id"])

    assert [item.order_id for item in result] == [
        newest_order["order_id"],
        first_order["order_id"],
    ]
