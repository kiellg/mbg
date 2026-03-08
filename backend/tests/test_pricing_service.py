"""Unit tests for the PricingService class in pricing_service.py."""
from dataclasses import dataclass
from decimal import Decimal

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
