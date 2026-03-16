# pylint: disable=protected-access
"""Unit tests for get_orders_assigned_to_driver in order_repo"""
from unittest.mock import patch
import pytest
from backend.app.data import order_data
from backend.app.repositories import order_repo


@pytest.fixture(autouse=True)
def reset_order_state():
    """Reset shared order state before each test"""
    original_db = order_data._ORDERDB.copy()
    original_next_id = order_data.NEXT_ORDER_ITEM_ID
    order_data._ORDERDB.clear()
    order_data.NEXT_ORDER_ITEM_ID = 1
    with patch.object(order_repo, "_alloc_order_id", return_value="order-1"):
        yield
    order_data._ORDERDB.clear()
    order_data._ORDERDB.update(original_db)
    order_data.NEXT_ORDER_ITEM_ID = original_next_id

def test_get_orders_assigned_to_driver_returns_matching_orders():
    """Should return only orders assigned to the given driver"""
    order_data._ORDERDB["order-1"] = {
        "order_id": "order-1",
        "driver_id": "Driver 1",
        "status": "Out for Delivery",
    }
    order_data._ORDERDB["order-2"] = {
        "order_id": "order-2",
        "driver_name": "Driver 2",
        "status": "Cooking",
    }

    result = order_repo.get_orders_assigned_to_driver("Driver 1")

    assert len(result) == 1
    assert result[0]["order_id"] == "order-1"

def test_get_orders_assigned_to_driver_returns_empty_when_no_match():
    """Should return empty list when no orders are assigned to the driver"""
    order_data._ORDERDB["order-1"] = {
        "order_id": "order-1",
        "driver_name": "Driver 2",
        "status": "Cooking",
    }

    result = order_repo.get_orders_assigned_to_driver("Driver 1")

    assert result == []

def test_create_order_record_stores_customer_phone():
    """Should store customer_phone when provided"""
    result = order_repo.create_order_record(
        customer_id="customer-1",
        restaurant_id=5,
        delivery_address="123 Test St",
        items=[{"quantity": 1, "item_price": "9.99"}],
        customer_phone="123-456-7890",
    )

    assert result["customer_phone"] == "123-456-7890"

def test_create_order_record_defaults_customer_phone_to_empty_string():
    """Should default customer_phone to empty string when not provided"""
    result = order_repo.create_order_record(
        customer_id="customer-1",
        restaurant_id=5,
        delivery_address="123 Test St",
        items=[{"quantity": 1, "item_price": "9.99"}],
    )

    assert result["customer_phone"] == ""
