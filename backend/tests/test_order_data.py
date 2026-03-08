"""Unit tests for order_data simulated database structure."""

# pylint: disable=protected-access
from backend.app.data import order_data


def setup_function():
    """Clear _ORDERDB before each test to ensure a clean state."""
    order_data._ORDERDB.clear()
    order_data.NEXT_ORDER_ID = 1
    order_data.NEXT_ORDER_ITEM_ID = 1


def test_orders_starts_empty():
    """Ensure the order database starts empty."""
    assert not order_data._ORDERDB


def test_order_record_shape():
    """Manually insert an order record and verify it matches the expected shape."""
    mock_order = {
        "order_id": 1,
        "status": "Pending",
        "delivery_address": "123 Main St",
        "subtotal": "0.00",
        "tax": "0.00",
        "delivery_fee": "0.00",
        "total": "0.00",
        "items": [
            {
                "order_item_id": 1,
                "order_id": 1,
                "quantity": 2,
                "item_price": "4.99",
            }
        ],
    }

    order_data._ORDERDB[1] = mock_order

    assert 1 in order_data._ORDERDB

    order = order_data._ORDERDB[1]
    assert "order_id" in order
    assert "status" in order
    assert "delivery_address" in order
    assert "subtotal" in order
    assert "tax" in order
    assert "delivery_fee" in order
    assert "total" in order
    assert "items" in order

    assert order["order_id"] == 1
    assert order["status"] == "Pending"
    assert order["delivery_address"] == "123 Main St"

    assert isinstance(order["items"], list)
    assert len(order["items"]) == 1

    item = order["items"][0]
    assert "order_item_id" in item
    assert "order_id" in item
    assert "quantity" in item
    assert "item_price" in item

    assert item["order_item_id"] == 1
    assert item["order_id"] == 1
    assert item["quantity"] == 2
    assert item["item_price"] == "4.99"


def test_multiple_orders_stored_independently():
    """Verify multiple orders can coexist without overwriting each other."""
    order_data._ORDERDB[1] = {
        "order_id": 1,
        "status": "Pending",
        "delivery_address": "A St",
        "subtotal": "0.00",
        "tax": "0.00",
        "delivery_fee": "0.00",
        "total": "0.00",
        "items": [{"order_item_id": 1, "order_id": 1, "quantity": 1, "item_price": "1.00"}],
    }

    order_data._ORDERDB[2] = {
        "order_id": 2,
        "status": "Cooking",
        "delivery_address": "B St",
        "subtotal": "0.00",
        "tax": "0.00",
        "delivery_fee": "0.00",
        "total": "0.00",
        "items": [{"order_item_id": 2, "order_id": 2, "quantity": 3, "item_price": "2.50"}],
    }

    assert len(order_data._ORDERDB) == 2
    assert order_data._ORDERDB[1]["delivery_address"] == "A St"
    assert order_data._ORDERDB[2]["delivery_address"] == "B St"


def test_create_order_record_allocates_ids_and_defaults():
    """Verify create_order_record allocates order_id/item ids and sets totals defaults."""
    created = order_data.create_order_record(
        delivery_address="123 Main St",
        items=[{"quantity": 2, "item_price": "4.99"}],
        status="Pending",
    )

    assert created["order_id"] == 1
    assert created["status"] == "Pending"
    assert created["delivery_address"] == "123 Main St"

    assert created["subtotal"] == "0.00"
    assert created["tax"] == "0.00"
    assert created["delivery_fee"] == "0.00"
    assert created["total"] == "0.00"

    assert isinstance(created["items"], list)
    assert len(created["items"]) == 1

    item = created["items"][0]
    assert item["order_item_id"] == 1
    assert item["order_id"] == 1
    assert item["quantity"] == 2
    assert item["item_price"] == "4.99"


def test_set_order_status_updates_existing_order():
    """Verify set_order_status updates status for an existing order."""
    order_data.create_order_record(
        delivery_address="123 Main St",
        items=[],
        status="Pending",
    )

    updated = order_data.set_order_status(1, "Cooking")
    assert updated is not None
    assert updated["status"] == "Cooking"


def test_cancel_order_record_sets_cancelled():
    """Verify cancel_order_record sets status to Cancelled."""
    order_data.create_order_record(
        delivery_address="123 Main St",
        items=[],
        status="Pending",
    )

    cancelled = order_data.cancel_order_record(1)
    assert cancelled is not None
    assert cancelled["status"] == "Cancelled"


def test_delete_order_record_removes_order():
    """Verify delete_order_record removes an order and returns True when it existed."""
    order_data.create_order_record(
        delivery_address="123 Main St",
        items=[],
        status="Pending",
    )

    assert 1 in order_data._ORDERDB
    assert order_data.delete_order_record(1) is True
    assert 1 not in order_data._ORDERDB


def test_delete_order_record_returns_false_when_missing():
    """Verify delete_order_record returns False when order does not exist."""
    assert order_data.delete_order_record(999) is False
