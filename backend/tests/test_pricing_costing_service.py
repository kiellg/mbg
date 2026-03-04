"""Unit tests for the PricingService class in pricing_costing_service.py."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

import pytest

from backend.app.services.pricing_costing_service import PricingService


TWOPLACES = Decimal("0.01")


"""Data classes for testing the PricingService."""
@dataclass
class OrderItem:
    order_item_id: int
    order_id: int
    quantity: int
    item_price: object

    """Calculate line total for an order item."""
    def get_line_total(self) -> Decimal:
        return (Decimal(str(self.item_price)) * Decimal(self.quantity)).quantize(
            TWOPLACES, rounding=ROUND_HALF_UP
        )

"""Data class for representing an order in tests."""
@dataclass
class Order: # pylint: disable=too-many-instance-attributes
    order_id: int
    status: str
    items: list[OrderItem]
    delivery_address: str
    subtotal: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    delivery_fee: object = Decimal("0.00")
    total: Decimal = Decimal("0.00")

    """Cancel the order by setting its status to 'Cancelled'."""
    def cancel(self):
        self.status = "Cancelled"

    """Update the order status to a new value."""
    def update_status(self, status: str):
        self.status = status

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

"""Test that calculate_totals handles an empty order with no items."""
def test_calculate_totals_empty_order():
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
