#pylint: disable=unused-argument
"""Unit tests for order_service.py with mocked repository calls."""

from decimal import Decimal
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from backend.app.services import order_service
from backend.app.schemas.order import (
    DeliveryMethod,
    OrderCreate,
    OrderItemCreate,
    OrderStatus,
    OrderUpdate,
)

FAKE_RAW_ORDER = {
    "order_id": "1",
    "customer_id": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
    "restaurant_id": 1,
    "status": "Pending",
    "delivery_address": "123 Test St",
    "delivery_method": "walk",
    "subtotal": "0.00",
    "tax": "0.00",
    "delivery_fee": "0.00",
    "total": "0.00",
    "items": [
        {"order_item_id": 1, "order_id": "1", "quantity": 2, "item_price": "10.00"}
    ],
}

FAKE_PAYLOAD = OrderCreate(
    customer_id="9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
    restaurant_id=1,
    delivery_address="123 Test St",
    delivery_method=DeliveryMethod.WALK,
    items=[OrderItemCreate(quantity=2, item_price=Decimal("10.00"))],
)

def _order_with_stringified_patch(patch: dict) -> dict:
    """Return a fake order merged with a stringified patch."""
    return {
        **FAKE_RAW_ORDER,
        **{key: str(value) for key, value in patch.items()},
    }

def _update_order_record_side_effect(_order_id: str, patch: dict) -> dict:
    """Mimic the repository updating an order record."""
    return _order_with_stringified_patch(patch)

# for create order
@patch("backend.app.services.order_service.PricingService.calculate_totals")
@patch("backend.app.services.order_service.order_repo")
def test_create_order_calls_repo_and_returns_response(mock_repo, mock_pricing):
    """Test that create_order calls the repository and returns an OrderResponse."""
    mock_repo.create_order_record.return_value = FAKE_RAW_ORDER
    mock_repo.update_order_record.return_value = FAKE_RAW_ORDER

    result = order_service.create_order(FAKE_PAYLOAD)

    mock_repo.create_order_record.assert_called_once()
    mock_repo.update_order_record.assert_called_once()
    assert result.order_id == "1"
    assert result.status == OrderStatus.PENDING

@patch("backend.app.services.order_service.PricingService.calculate_totals")
@patch("backend.app.services.order_service.order_repo")
def test_create_order_calls_pricing_service(mock_repo, mock_pricing):
    """Test that create_order calls the PricingService to calculate totals."""
    mock_repo.create_order_record.return_value = FAKE_RAW_ORDER
    mock_repo.update_order_record.return_value = FAKE_RAW_ORDER

    order_service.create_order(FAKE_PAYLOAD)

    mock_pricing.assert_called_once()

@patch("backend.app.services.order_service.order_repo")
def test_create_order_persists_recalculated_totals(mock_repo):
    """Test that create_order stores recalculated totals before returning."""
    mock_repo.create_order_record.return_value = FAKE_RAW_ORDER
    mock_repo.update_order_record.side_effect = _update_order_record_side_effect

    result = order_service.create_order(FAKE_PAYLOAD)

    patch = mock_repo.update_order_record.call_args[0][1]
    assert patch["subtotal"] == Decimal("20.00")
    assert patch["tax"] == Decimal("2.00")
    assert patch["delivery_fee"] == Decimal("5.00")
    assert patch["total"] == Decimal("27.00")
    assert result.total == Decimal("27.00")

# for get order
@patch("backend.app.services.order_service.order_repo")
def test_get_order_returns_order(mock_repo):
    """Test that get_order returns an OrderResponse when the order exists."""
    mock_repo.get_order_record.return_value = FAKE_RAW_ORDER

    result = order_service.get_order(1)

    mock_repo.get_order_record.assert_called_once_with(1)
    assert result.order_id == "1"

@patch("backend.app.services.order_service.PricingService.calculate_totals")
@patch("backend.app.services.order_service.order_repo")
def test_get_order_uses_stored_totals(mock_repo, mock_pricing):
    """Test that get_order returns stored totals without recalculating."""
    mock_repo.get_order_record.return_value = {
        **FAKE_RAW_ORDER,
        "subtotal": "99.99",
        "tax": "1.23",
        "delivery_fee": "4.56",
        "total": "105.78",
    }

    result = order_service.get_order("1")

    mock_pricing.assert_not_called()
    assert result.subtotal == Decimal("99.99")
    assert result.tax == Decimal("1.23")
    assert result.delivery_fee == Decimal("4.56")
    assert result.total == Decimal("105.78")

@patch("backend.app.services.order_service.order_repo")
def test_get_order_raises_404_if_not_found(mock_repo):
    """Test that get_order raises a 404 HTTPException when the order is not found."""
    mock_repo.get_order_record.return_value = None

    with pytest.raises(HTTPException) as exc:
        order_service.get_order("99")

    assert exc.value.status_code == 404

# for list orders
@patch("backend.app.services.order_service.order_repo")
def test_list_orders_returns_all(mock_repo):
    """Test that list_orders returns a list of OrderResponse objects for all orders."""
    mock_repo.list_order_records.return_value = [FAKE_RAW_ORDER, FAKE_RAW_ORDER]

    result = order_service.list_orders()

    assert len(result) == 2

@patch("backend.app.services.order_service.order_repo")
def test_list_orders_returns_empty_list(mock_repo):
    """Test that list_orders returns an empty list when there are no orders."""
    mock_repo.list_order_records.return_value = []

    result = order_service.list_orders()

    assert not result

# for update order
@patch("backend.app.services.order_service.PricingService.calculate_totals")
@patch("backend.app.services.order_service.order_repo")
def test_update_order_returns_updated_order(mock_repo, mock_pricing):
    """Test that update_order returns an OrderResponse with the updated status."""
    mock_repo.get_order_record.return_value = FAKE_RAW_ORDER
    mock_repo.update_order_record.return_value = {**FAKE_RAW_ORDER, "status": "Cooking"}

    result = order_service.update_order(1, OrderUpdate(status=OrderStatus.COOKING))

    mock_repo.update_order_record.assert_called_once()
    assert result.status == OrderStatus.COOKING

@patch("backend.app.services.order_service.order_repo")
def test_update_order_recalculates_totals_while_pending(mock_repo):
    """Test that update_order stores recalculated totals when the order is pending."""
    mock_repo.get_order_record.return_value = FAKE_RAW_ORDER
    mock_repo.update_order_record.side_effect = _update_order_record_side_effect

    result = order_service.update_order(1, OrderUpdate(delivery_method=DeliveryMethod.CAR))

    patch = mock_repo.update_order_record.call_args[0][1]
    assert patch["delivery_method"] == DeliveryMethod.CAR.value
    assert patch["subtotal"] == Decimal("20.00")
    assert patch["tax"] == Decimal("2.00")
    assert patch["delivery_fee"] == Decimal("10.00")
    assert patch["total"] == Decimal("32.00")
    assert result.total == Decimal("32.00")

@patch("backend.app.services.order_service.order_repo")
def test_update_order_raises_400_if_not_pending(mock_repo):
    """Test that update_order rejects changes when the order is not pending."""
    statuses = [
        OrderStatus.COOKING.value,
        OrderStatus.OUT_FOR_DELIVERY.value,
        OrderStatus.DELIVERED.value,
        OrderStatus.CANCELLED.value,
    ]

    for status in statuses:
        mock_repo.reset_mock()
        mock_repo.get_order_record.return_value = {**FAKE_RAW_ORDER, "status": status}

        with pytest.raises(HTTPException) as exc:
            order_service.update_order(1, OrderUpdate(delivery_address="456 New St"))

        assert exc.value.status_code == 400
        mock_repo.update_order_record.assert_not_called()

@patch("backend.app.services.order_service.order_repo")
def test_update_order_raises_404_if_not_found(mock_repo):
    """Test that update_order raises a 404 HTTPException when the order is not found."""
    mock_repo.get_order_record.return_value = None

    with pytest.raises(HTTPException) as exc:
        order_service.update_order(99, OrderUpdate(status=OrderStatus.COOKING))

    assert exc.value.status_code == 404

# for cancel order
@patch("backend.app.services.order_service.order_repo")
def test_cancel_order_returns_cancelled_order(mock_repo):
    """Test that cancel_order returns an OrderResponse with status set to Cancelled."""
    mock_repo.get_order_record.return_value = FAKE_RAW_ORDER
    mock_repo.cancel_order_record.return_value = {**FAKE_RAW_ORDER, "status": "Cancelled"}

    result = order_service.cancel_order("1")

    mock_repo.cancel_order_record.assert_called_once_with("1")
    assert result.status == OrderStatus.CANCELLED

@patch("backend.app.services.order_service.order_repo")
def test_cancel_order_raises_404_if_not_found(mock_repo):
    """Test that cancel_order raises a 404 HTTPException when the order is not found."""
    mock_repo.get_order_record.return_value = None

    with pytest.raises(HTTPException) as exc:
        order_service.cancel_order("99")

    assert exc.value.status_code == 404

@patch("backend.app.services.order_service.order_repo")
def test_cancel_order_raises_400_if_not_pending(mock_repo):
    """Test that cancel_order rejects non-pending orders."""
    statuses = [
        OrderStatus.COOKING.value,
        OrderStatus.OUT_FOR_DELIVERY.value,
        OrderStatus.DELIVERED.value,
        OrderStatus.CANCELLED.value,
    ]

    for status in statuses:
        mock_repo.reset_mock()
        mock_repo.get_order_record.return_value = {**FAKE_RAW_ORDER, "status": status}

        with pytest.raises(HTTPException) as exc:
            order_service.cancel_order("1")

        assert exc.value.status_code == 400
        mock_repo.cancel_order_record.assert_not_called()

# for delete order
@patch("backend.app.services.order_service.order_repo")
def test_delete_order_raises_400(mock_repo):
    """Test that delete_order is rejected."""
    mock_repo.get_order_record.return_value = FAKE_RAW_ORDER

    with pytest.raises(HTTPException) as exc:
        order_service.delete_order("1")

    assert exc.value.status_code == 400
    mock_repo.delete_order_record.assert_not_called()

@patch("backend.app.services.order_service.order_repo")
def test_delete_order_raises_404_if_not_found(mock_repo):
    """Test that delete_order raises a 404 HTTPException when the order is not found."""
    mock_repo.get_order_record.return_value = None

    with pytest.raises(HTTPException) as exc:
        order_service.delete_order("99")

    assert exc.value.status_code == 404
