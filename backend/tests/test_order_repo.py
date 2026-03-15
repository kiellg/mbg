# pylint: disable=protected-access
"""Unit tests for order_repo.py"""

import pytest

from backend.app.data import order_data
from backend.app.repositories import order_repo


@pytest.fixture(autouse=True)
def reset_order_state(monkeypatch):
    """Reset shared order state before each test and restore it afterward."""
    original_db = order_data._ORDERDB.copy()
    original_next_order_item_id = order_data.NEXT_ORDER_ITEM_ID

    order_data._ORDERDB.clear()
    order_data.NEXT_ORDER_ITEM_ID = 1
    monkeypatch.setattr(order_repo, "_alloc_order_id", lambda: "order-1")

    yield

    order_data._ORDERDB.clear()
    order_data._ORDERDB.update(original_db)
    order_data.NEXT_ORDER_ITEM_ID = original_next_order_item_id


def test_get_order_record_returns_none_for_missing_order_id():
    """Should return None when the order does not exist."""
    result = order_repo.get_order_record("missing")

    assert result is None


def test_get_order_record_returns_existing_order():
    """Should return the stored order record for an existing order."""
    order = order_repo.create_order_record(
        customer_id="customer-1",
        restaurant_id=5,
        delivery_address="123 Test St",
        items=[{"quantity": 2, "item_price": "12.50"}],
    )

    result = order_repo.get_order_record("order-1")

    assert result == order


def test_list_order_records_returns_empty_list_when_db_is_empty():
    """Should return an empty list when there are no stored orders."""
    result = order_repo.list_order_records()

    assert result == []


def test_list_order_records_returns_all_orders_sorted_by_order_id():
    """Should return all orders sorted by order_id."""
    order_data._ORDERDB["order-b"] = {"order_id": "order-b"}
    order_data._ORDERDB["order-a"] = {"order_id": "order-a"}
    order_data._ORDERDB["order-c"] = {"order_id": "order-c"}

    result = order_repo.list_order_records()

    assert [order["order_id"] for order in result] == ["order-a", "order-b", "order-c"]


def test_create_order_record_creates_and_stores_order_with_defaults():
    """Should create and store a new order with expected default fields."""
    result = order_repo.create_order_record(
        customer_id="customer-1",
        restaurant_id=5,
        delivery_address="123 Test St",
        items=[{"quantity": 1, "item_price": 9.99}],
    )

    assert result["order_id"] == "order-1"
    assert result["customer_id"] == "customer-1"
    assert result["restaurant_id"] == 5
    assert result["delivery_address"] == "123 Test St"
    assert result["delivery_method"] == "walk"
    assert result["status"] == "Pending"
    assert result["subtotal"] == "0.00"
    assert result["tax"] == "0.00"
    assert result["delivery_fee"] == "0.00"
    assert result["total"] == "0.00"
    assert result["items"][0]["order_item_id"] == 1
    assert result["items"][0]["order_id"] == "order-1"
    assert result["items"][0]["quantity"] == 1
    assert result["items"][0]["item_price"] == "9.99"
    assert order_data._ORDERDB["order-1"] == result


def test_create_order_record_supports_custom_delivery_method_and_status():
    """Should store custom delivery_method and status values."""
    result = order_repo.create_order_record(
        customer_id="customer-1",
        restaurant_id=5,
        delivery_address="123 Test St",
        items=[{"quantity": 2, "item_price": "12.50"}],
        delivery_method="car",
        status="Cooking",
    )

    assert result["delivery_method"] == "car"
    assert result["status"] == "Cooking"
    assert result["items"][0]["item_price"] == "12.50"


def test_create_order_record_raises_value_error_when_item_is_missing_quantity():
    """Should raise ValueError when an item does not include quantity."""
    with pytest.raises(ValueError):
        order_repo.create_order_record(
            customer_id="customer-1",
            restaurant_id=5,
            delivery_address="123 Test St",
            items=[{"item_price": "12.50"}],
        )


def test_create_order_record_raises_value_error_when_item_is_missing_item_price():
    """Should raise ValueError when an item does not include item_price."""
    with pytest.raises(ValueError):
        order_repo.create_order_record(
            customer_id="customer-1",
            restaurant_id=5,
            delivery_address="123 Test St",
            items=[{"quantity": 2}],
        )


def test_update_order_record_returns_none_for_missing_order_id():
    """Should return None when trying to update a missing order."""
    result = order_repo.update_order_record("missing", {"status": "Cooking"})

    assert result is None


def test_update_order_record_updates_only_provided_scalar_fields():
    """Should update only the scalar fields included in the patch."""
    order_repo.create_order_record(
        customer_id="customer-1",
        restaurant_id=5,
        delivery_address="123 Test St",
        items=[{"quantity": 2, "item_price": "12.50"}],
    )

    result = order_repo.update_order_record(
        "order-1",
        {
            "status": "Cooking",
            "delivery_address": "456 New St",
            "subtotal": 25.00,
            "tax": 2.50,
            "delivery_fee": 5.00,
            "total": 32.50,
        },
    )

    assert result["status"] == "Cooking"
    assert result["delivery_address"] == "456 New St"
    assert result["subtotal"] == "25.00"
    assert result["tax"] == "2.50"
    assert result["delivery_fee"] == "5.00"
    assert result["total"] == "32.50"
    assert result["customer_id"] == "customer-1"
    assert result["restaurant_id"] == 5
    assert result["delivery_method"] == "walk"
    assert result["items"][0]["order_item_id"] == 1


def test_update_order_record_replaces_items_and_preserves_provided_order_item_id():
    """Should replace items and keep a provided order_item_id."""
    order_repo.create_order_record(
        customer_id="customer-1",
        restaurant_id=5,
        delivery_address="123 Test St",
        items=[{"quantity": 2, "item_price": "12.50"}],
    )

    result = order_repo.update_order_record(
        "order-1",
        {"items": [{"order_item_id": 99, "quantity": 3, "item_price": "7.50"}]},
    )

    assert len(result["items"]) == 1
    assert result["items"][0]["order_item_id"] == 99
    assert result["items"][0]["order_id"] == "order-1"
    assert result["items"][0]["quantity"] == 3
    assert result["items"][0]["item_price"] == "7.50"


def test_update_order_record_allocates_new_order_item_id_when_missing():
    """Should allocate a new order_item_id for patched items when one is not provided."""
    order_repo.create_order_record(
        customer_id="customer-1",
        restaurant_id=5,
        delivery_address="123 Test St",
        items=[{"quantity": 2, "item_price": "12.50"}],
    )

    result = order_repo.update_order_record(
        "order-1",
        {"items": [{"quantity": 1, "item_price": 9.99}]},
    )

    assert len(result["items"]) == 1
    assert result["items"][0]["order_item_id"] == 2
    assert result["items"][0]["order_id"] == "order-1"
    assert result["items"][0]["quantity"] == 1
    assert result["items"][0]["item_price"] == "9.99"
    assert order_data.NEXT_ORDER_ITEM_ID == 3


def test_update_order_record_raises_value_error_when_patched_item_is_missing_quantity():
    """Should raise ValueError when a patched item does not include quantity."""
    order_repo.create_order_record(
        customer_id="customer-1",
        restaurant_id=5,
        delivery_address="123 Test St",
        items=[{"quantity": 2, "item_price": "12.50"}],
    )

    with pytest.raises(ValueError):
        order_repo.update_order_record(
            "order-1",
            {"items": [{"item_price": "12.50"}]},
        )


def test_update_order_record_raises_value_error_when_patched_item_is_missing_item_price():
    """Should raise ValueError when a patched item does not include item_price."""
    order_repo.create_order_record(
        customer_id="customer-1",
        restaurant_id=5,
        delivery_address="123 Test St",
        items=[{"quantity": 2, "item_price": "12.50"}],
    )

    with pytest.raises(ValueError):
        order_repo.update_order_record(
            "order-1",
            {"items": [{"quantity": 2}]},
        )


def test_set_order_status_updates_status():
    """Should update the status of an existing order."""
    order_repo.create_order_record(
        customer_id="customer-1",
        restaurant_id=5,
        delivery_address="123 Test St",
        items=[{"quantity": 2, "item_price": "12.50"}],
    )

    result = order_repo.set_order_status("order-1", "Delivered")

    assert result["status"] == "Delivered"

 
def test_set_order_status_returns_none_for_missing_order_id():
    """Should return None when the order does not exist."""
    result = order_repo.set_order_status("missing", "Delivered")

    assert result is None


def test_cancel_order_record_sets_status_to_cancelled():
    """Should set the status to Cancelled."""
    order_repo.create_order_record(
        customer_id="customer-1",
        restaurant_id=5,
        delivery_address="123 Test St",
        items=[{"quantity": 2, "item_price": "12.50"}],
    )

    result = order_repo.cancel_order_record("order-1")

    assert result["status"] == "Cancelled"


def test_cancel_order_record_returns_none_for_missing_order_id():
    """Should return None when the order does not exist."""
    result = order_repo.cancel_order_record("missing")

    assert result is None
