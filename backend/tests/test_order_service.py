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
    delivery_address="123 Test St",
    delivery_method=DeliveryMethod.WALK,
    items=[OrderItemCreate(quantity=2, item_price=Decimal("10.00"))],
)

# for create order
@patch("backend.app.services.order_service.PricingService.calculate_totals")
@patch("backend.app.services.order_service.order_repo")
def test_create_order_calls_repo_and_returns_response(mock_repo, mock_pricing):
    """Test that create_order calls the repository and returns an OrderResponse."""
    mock_repo.create_order_record.return_value = FAKE_RAW_ORDER

    result = order_service.create_order(FAKE_PAYLOAD)

    mock_repo.create_order_record.assert_called_once()
    assert result.order_id == "1"
    assert result.status == OrderStatus.PENDING

@patch("backend.app.services.order_service.PricingService.calculate_totals")
@patch("backend.app.services.order_service.order_repo")
def test_create_order_calls_pricing_service(mock_repo, mock_pricing):
    """Test that create_order calls the PricingService to calculate totals."""
    mock_repo.create_order_record.return_value = FAKE_RAW_ORDER

    order_service.create_order(FAKE_PAYLOAD)

    mock_pricing.assert_called_once()

# for get order
@patch("backend.app.services.order_service.PricingService.calculate_totals")
@patch("backend.app.services.order_service.order_repo")
def test_get_order_returns_order(mock_repo, mock_pricing):
    """Test that get_order returns an OrderResponse when the order exists."""
    mock_repo.get_order_record.return_value = FAKE_RAW_ORDER

    result = order_service.get_order(1)

    mock_repo.get_order_record.assert_called_once_with(1)
    assert result.order_id == "1"

@patch("backend.app.services.order_service.order_repo")
def test_get_order_raises_404_if_not_found(mock_repo):
    """Test that get_order raises a 404 HTTPException when the order is not found."""
    mock_repo.get_order_record.return_value = None

    with pytest.raises(HTTPException) as exc:
        order_service.get_order(99)

    assert exc.value.status_code == 404

# for list orders
@patch("backend.app.services.order_service.PricingService.calculate_totals")
@patch("backend.app.services.order_service.order_repo")
def test_list_orders_returns_all(mock_repo, mock_pricing):
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
def test_update_order_raises_404_if_not_found(mock_repo):
    """Test that update_order raises a 404 HTTPException when the order is not found."""
    mock_repo.get_order_record.return_value = None

    with pytest.raises(HTTPException) as exc:
        order_service.update_order(99, OrderUpdate(status=OrderStatus.COOKING))

    assert exc.value.status_code == 404

# for cancel order
@patch("backend.app.services.order_service.PricingService.calculate_totals")
@patch("backend.app.services.order_service.order_repo")
def test_cancel_order_returns_cancelled_order(mock_repo, mock_pricing):
    """Test that cancel_order returns an OrderResponse with status set to Cancelled."""
    mock_repo.cancel_order_record.return_value = {**FAKE_RAW_ORDER, "status": "Cancelled"}

    result = order_service.cancel_order(1)

    mock_repo.cancel_order_record.assert_called_once_with(1)
    assert result.status == OrderStatus.CANCELLED

@patch("backend.app.services.order_service.order_repo")
def test_cancel_order_raises_404_if_not_found(mock_repo):
    """Test that cancel_order raises a 404 HTTPException when the order is not found."""
    mock_repo.cancel_order_record.return_value = None

    with pytest.raises(HTTPException) as exc:
        order_service.cancel_order(99)

    assert exc.value.status_code == 404

# for delete order
@patch("backend.app.services.order_service.order_repo")
def test_delete_order_calls_repo(mock_repo):
    """Test that delete_order calls the repository to delete the order."""
    mock_repo.delete_order_record.return_value = True

    order_service.delete_order(1)

    mock_repo.delete_order_record.assert_called_once_with(1)

@patch("backend.app.services.order_service.order_repo")
def test_delete_order_raises_404_if_not_found(mock_repo):
    """Test that delete_order raises a 404 HTTPException when the order is not found."""
    mock_repo.delete_order_record.return_value = False

    with pytest.raises(HTTPException) as exc:
        order_service.delete_order(99)

    assert exc.value.status_code == 404
