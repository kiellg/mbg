"""Unit tests for the PricingService class in pricing_service.py."""
from dataclasses import dataclass
from decimal import Decimal

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
    subtotal: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    delivery_fee: object = Decimal("0.00")
    tax_rate: object = Decimal("0.10")
    total: Decimal = Decimal("0.00")


def test_calculate_totals_basic():
    """Test that calculate_totals correctly computes subtotal, tax, and total for a simple order."""
    order = Order(
        order_id=1,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=1, quantity=2, item_price="10.00"),
            OrderItem(order_item_id=2, order_id=1, quantity=1, item_price="3.50"),
        ],
        delivery_address="123 Main St",
        delivery_fee="2.00",
    )

    PricingService.calculate_totals(order)

    assert order.subtotal == Decimal("23.50")
    assert order.delivery_fee == Decimal("2.00")
    assert order.tax == Decimal("2.35")
    assert order.total == Decimal("27.85")


def test_calculate_totals_empty_order():
    """Test that calculate_totals handles an empty order with no items."""
    order = Order(
        order_id=2,
        status="Pending",
        items=[],
        delivery_address="123 Main St",
        delivery_fee="4.99",
    )

    PricingService.calculate_totals(order)

    assert order.subtotal == Decimal("0.00")
    assert order.delivery_fee == Decimal("4.99")
    assert order.tax == Decimal("0.00")
    assert order.total == Decimal("4.99")


def test_calculate_totals_applies_default_tax_rule():
    """Tests PricingService applies the predefined tax rate to subtotal and includes it in total."""
    order = Order(
        order_id=3,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=3, quantity=2, item_price="15.00"),
        ],
        delivery_address="123 Main St",
        delivery_fee="5.00",
    )

    PricingService.calculate_totals(order)

    assert order.subtotal == Decimal("30.00")
    assert order.tax == Decimal("3.00")   # 10% of 30.00
    assert order.total == Decimal("38.00")  # 30.00 + 5.00 + 3.00


def test_calculate_totals_rejects_none_order():
    """Test that calculate_totals rejects a missing order."""
    with pytest.raises(ValueError, match="Order is required"):
        PricingService.calculate_totals(None)


def test_calculate_totals_rejects_missing_items():
    """Test that calculate_totals rejects an order with missing items."""
    order = Order(
        order_id=4,
        status="Pending",
        items=None,
        delivery_address="123 Main St",
        delivery_fee="2.00",
    )

    with pytest.raises(ValueError, match="Order items are required"):
        PricingService.calculate_totals(order)


def test_calculate_totals_rejects_none_item():
    """Test that calculate_totals rejects a missing order item."""
    order = Order(
        order_id=5,
        status="Pending",
        items=[None],
        delivery_address="123 Main St",
        delivery_fee="2.00",
    )

    with pytest.raises(ValueError, match="Order item is required"):
        PricingService.calculate_totals(order)


def test_calculate_totals_rejects_none_quantity():
    """Test that calculate_totals rejects an item with a missing quantity."""
    order = Order(
        order_id=6,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=6, quantity=None, item_price="10.00"),
        ],
        delivery_address="123 Main St",
        delivery_fee="2.00",
    )

    with pytest.raises(ValueError, match="Order item quantity is required"):
        PricingService.calculate_totals(order)


def test_calculate_totals_rejects_zero_quantity():
    """Test that calculate_totals rejects an item with zero quantity."""
    order = Order(
        order_id=7,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=7, quantity=0, item_price="10.00"),
        ],
        delivery_address="123 Main St",
        delivery_fee="2.00",
    )

    with pytest.raises(ValueError, match="Order item quantity must be greater than zero"):
        PricingService.calculate_totals(order)


def test_calculate_totals_rejects_negative_quantity():
    """Test that calculate_totals rejects an item with a negative quantity."""
    order = Order(
        order_id=8,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=8, quantity=-1, item_price="10.00"),
        ],
        delivery_address="123 Main St",
        delivery_fee="2.00",
    )

    with pytest.raises(ValueError, match="Order item quantity must be greater than zero"):
        PricingService.calculate_totals(order)


def test_calculate_totals_rejects_none_item_price():
    """Test that calculate_totals rejects an item with a missing price."""
    order = Order(
        order_id=9,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=9, quantity=1, item_price=None),
        ],
        delivery_address="123 Main St",
        delivery_fee="2.00",
    )

    with pytest.raises(ValueError, match="Order item price is required"):
        PricingService.calculate_totals(order)


def test_calculate_totals_rejects_invalid_item_price():
    """Test that calculate_totals rejects an item with a non-numeric price."""
    order = Order(
        order_id=10,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=10, quantity=1, item_price="abc"),
        ],
        delivery_address="123 Main St",
        delivery_fee="2.00",
    )

    with pytest.raises(ValueError, match="Order item price must be a valid number"):
        PricingService.calculate_totals(order)


def test_calculate_totals_rejects_negative_item_price():
    """Test that calculate_totals rejects an item with a negative price."""
    order = Order(
        order_id=11,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=11, quantity=1, item_price="-5.00"),
        ],
        delivery_address="123 Main St",
        delivery_fee="2.00",
    )

    with pytest.raises(ValueError, match="Order item price cannot be negative"):
        PricingService.calculate_totals(order)


def test_calculate_totals_rejects_invalid_delivery_fee():
    """Test that calculate_totals rejects a non-numeric delivery fee."""
    order = Order(
        order_id=12,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=12, quantity=1, item_price="10.00"),
        ],
        delivery_address="123 Main St",
        delivery_fee="abc",
    )

    with pytest.raises(ValueError, match="Delivery fee must be a valid number"):
        PricingService.calculate_totals(order)


def test_calculate_totals_rejects_negative_delivery_fee():
    """Test that calculate_totals rejects a negative delivery fee."""
    order = Order(
        order_id=13,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=13, quantity=1, item_price="10.00"),
        ],
        delivery_address="123 Main St",
        delivery_fee="-1.00",
    )

    with pytest.raises(ValueError, match="Delivery fee cannot be negative"):
        PricingService.calculate_totals(order)


def test_calculate_totals_rejects_invalid_tax_rate():
    """Test that calculate_totals rejects a non-numeric tax rate."""
    order = Order(
        order_id=14,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=14, quantity=1, item_price="10.00"),
        ],
        delivery_address="123 Main St",
        delivery_fee="2.00",
        tax_rate="abc",
    )

    with pytest.raises(ValueError, match="Tax rate must be a valid number"):
        PricingService.calculate_totals(order)


def test_calculate_totals_rejects_negative_tax_rate():
    """Test that calculate_totals rejects a negative tax rate."""
    order = Order(
        order_id=15,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=15, quantity=1, item_price="10.00"),
        ],
        delivery_address="123 Main St",
        delivery_fee="2.00",
        tax_rate="-0.10",
    )

    with pytest.raises(ValueError, match="Tax rate cannot be negative"):
        PricingService.calculate_totals(order)
