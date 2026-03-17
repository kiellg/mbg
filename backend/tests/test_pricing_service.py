"""Unit tests for the PricingService class in pricing_service.py."""

from dataclasses import dataclass
from decimal import Decimal
from unittest.mock import patch

import pytest

from backend.app.services.pricing_service import PricingService


@dataclass
class OrderItem:
    """Minimal order item model used by pricing service tests."""

    order_item_id: int
    order_id: int
    quantity: int
    item_price: object


@dataclass
class Order:  # pylint: disable=too-many-instance-attributes
    """Minimal order model with pricing fields mutated by PricingService."""

    order_id: int
    status: str
    items: list[OrderItem]
    delivery_address: str
    delivery_method: object = "walk"
    subtotal: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    tax_rate: object = Decimal("0.10")
    delivery_fee: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")


def test_calculate_totals_basic_walk_delivery():
    """Test subtotal, tax, delivery fee, and total for a walk delivery order."""
    order = Order(
        order_id=1,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=1, quantity=2, item_price="10.00"),
            OrderItem(order_item_id=2, order_id=1, quantity=1, item_price="3.50"),
        ],
        delivery_address="123 Main St",
        delivery_method="walk",
    )

    PricingService.calculate_totals(order)

    assert order.subtotal == Decimal("23.50")
    assert order.delivery_fee == Decimal("5.00")
    assert order.tax == Decimal("2.35")
    assert order.total == Decimal("30.85")


@patch("backend.app.services.pricing_service.PricingService._validate_tax_rate")
@patch("backend.app.services.pricing_service.PricingService.calculate_delivery_fee")
@patch("backend.app.services.pricing_service.PricingService._validate_item")
@patch("backend.app.services.pricing_service.PricingService._validate_order")
def test_calculate_totals_uses_helpers_and_updates_order_fields(
    mock_validate_order,
    mock_validate_item,
    mock_calculate_delivery_fee,
    mock_validate_tax_rate,
):
    """calculate_totals should use its helpers and still update pricing fields."""
    order = Order(
        order_id=2,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=2, quantity=2, item_price="10.00"),
            OrderItem(order_item_id=2, order_id=2, quantity=1, item_price="3.50"),
        ],
        delivery_address="123 Main St",
        delivery_method="walk",
    )
    mock_validate_item.side_effect = [
        (2, Decimal("10.00")),
        (1, Decimal("3.50")),
    ]
    mock_calculate_delivery_fee.return_value = Decimal("5.00")
    mock_validate_tax_rate.return_value = Decimal("0.10")

    PricingService.calculate_totals(order)

    mock_validate_order.assert_called_once_with(order)
    assert mock_validate_item.call_count == 2
    mock_calculate_delivery_fee.assert_called_once_with("walk")
    mock_validate_tax_rate.assert_called_once_with(order)
    assert order.subtotal == Decimal("23.50")
    assert order.delivery_fee == Decimal("5.00")
    assert order.tax == Decimal("2.35")
    assert order.total == Decimal("30.85")


def test_calculate_totals_empty_order_bike_delivery():
    """Test an empty order still applies bike fixed delivery fee."""
    order = Order(
        order_id=3,
        status="Pending",
        items=[],
        delivery_address="123 Main St",
        delivery_method="bike",
    )

    PricingService.calculate_totals(order)

    assert order.subtotal == Decimal("0.00")
    assert order.delivery_fee == Decimal("8.00")
    assert order.tax == Decimal("0.00")
    assert order.total == Decimal("8.00")


def test_calculate_totals_applies_default_tax_rule_with_car_delivery():
    """Test default tax is applied and total includes fixed car delivery fee."""
    order = Order(
        order_id=4,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=4, quantity=2, item_price="15.00"),
        ],
        delivery_address="123 Main St",
        delivery_method="car",
    )

    PricingService.calculate_totals(order)

    assert order.subtotal == Decimal("30.00")
    assert order.delivery_fee == Decimal("10.00")
    assert order.tax == Decimal("3.00")
    assert order.total == Decimal("43.00")


def test_calculate_delivery_fee_walk():
    """Test walk delivery method applies the fixed 5.00 delivery fee."""
    assert PricingService.calculate_delivery_fee("walk") == Decimal("5.00")


def test_calculate_delivery_fee_bike():
    """Test bike delivery method applies the fixed 8.00 delivery fee."""
    assert PricingService.calculate_delivery_fee("bike") == Decimal("8.00")


def test_calculate_delivery_fee_car():
    """Test car delivery method applies the fixed 10.00 delivery fee."""
    assert PricingService.calculate_delivery_fee("car") == Decimal("10.00")


def test_validate_order_rejects_none_order():
    """Test that order validation rejects a missing order."""
    with pytest.raises(ValueError, match="Order is required"):
        PricingService._validate_order(None)


def test_validate_order_rejects_missing_items():
    """Test that order validation rejects an order with missing items."""
    order = Order(
        order_id=5,
        status="Pending",
        items=None,
        delivery_address="123 Main St",
        delivery_method="walk",
    )

    with pytest.raises(ValueError, match="Order items are required"):
        PricingService._validate_order(order)


def test_validate_item_rejects_none_item():
    """Test that item validation rejects a missing order item."""
    with pytest.raises(ValueError, match="Order item is required"):
        PricingService._validate_item(None)


def test_validate_item_rejects_none_quantity():
    """Test that item validation rejects an item with a missing quantity."""
    item = OrderItem(order_item_id=1, order_id=6, quantity=None, item_price="10.00")

    with pytest.raises(ValueError, match="Order item quantity is required"):
        PricingService._validate_item(item)


def test_validate_item_rejects_zero_quantity():
    """Test that item validation rejects an item with zero quantity."""
    item = OrderItem(order_item_id=1, order_id=7, quantity=0, item_price="10.00")

    with pytest.raises(ValueError, match="Order item quantity must be greater than zero"):
        PricingService._validate_item(item)


def test_validate_item_rejects_negative_quantity():
    """Test that item validation rejects an item with a negative quantity."""
    item = OrderItem(order_item_id=1, order_id=8, quantity=-1, item_price="10.00")

    with pytest.raises(ValueError, match="Order item quantity must be greater than zero"):
        PricingService._validate_item(item)


def test_validate_item_rejects_none_item_price():
    """Test that item validation rejects an item with a missing price."""
    item = OrderItem(order_item_id=1, order_id=9, quantity=1, item_price=None)

    with pytest.raises(ValueError, match="Order item price is required"):
        PricingService._validate_item(item)


def test_validate_item_rejects_invalid_item_price():
    """Test that item validation rejects an item with a non-numeric price."""
    item = OrderItem(order_item_id=1, order_id=10, quantity=1, item_price="abc")

    with pytest.raises(ValueError, match="Order item price must be a valid number"):
        PricingService._validate_item(item)


def test_validate_item_rejects_negative_item_price():
    """Test that item validation rejects an item with a negative price."""
    item = OrderItem(order_item_id=1, order_id=11, quantity=1, item_price="-5.00")

    with pytest.raises(ValueError, match="Order item price cannot be negative"):
        PricingService._validate_item(item)


def test_validate_tax_rate_rejects_invalid_tax_rate():
    """Test that tax-rate validation rejects a non-numeric tax rate."""
    order = Order(
        order_id=12,
        status="Pending",
        items=[OrderItem(order_item_id=1, order_id=12, quantity=1, item_price="10.00")],
        delivery_address="123 Main St",
        delivery_method="walk",
        tax_rate="abc",
    )

    with pytest.raises(ValueError, match="Tax rate must be a valid number"):
        PricingService._validate_tax_rate(order)


def test_validate_tax_rate_rejects_negative_tax_rate():
    """Test that tax-rate validation rejects a negative tax rate."""
    order = Order(
        order_id=13,
        status="Pending",
        items=[OrderItem(order_item_id=1, order_id=13, quantity=1, item_price="10.00")],
        delivery_address="123 Main St",
        delivery_method="walk",
        tax_rate="-0.10",
    )

    with pytest.raises(ValueError, match="Tax rate cannot be negative"):
        PricingService._validate_tax_rate(order)


def test_calculate_delivery_fee_rejects_invalid_delivery_method():
    """Test that delivery fee calculation rejects an unsupported delivery method."""
    with pytest.raises(ValueError, match="Delivery method must be one of: walk, bike, car"):
        PricingService.calculate_delivery_fee("plane")


def test_calculate_delivery_fee_rejects_missing_delivery_method():
    """Test that delivery fee calculation rejects a missing delivery method."""
    with pytest.raises(ValueError, match="Delivery method is required"):
        PricingService.calculate_delivery_fee(None)
