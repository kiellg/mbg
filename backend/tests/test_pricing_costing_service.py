from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

import pytest

from backend.app.services.pricing_costing_service import PricingService


TWOPLACES = Decimal("0.01")


@dataclass
class OrderItem:
    orderItemId: int
    orderId: int
    quantity: int
    itemPrice: object

    def getLineTotal(self) -> Decimal:
        return (Decimal(str(self.itemPrice)) * Decimal(self.quantity)).quantize(
            TWOPLACES, rounding=ROUND_HALF_UP
        )


@dataclass
class Order:
    orderId: int
    status: str
    items: list[OrderItem]
    deliveryAddress: str
    subtotal: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    deliveryFee: object = Decimal("0.00")
    total: Decimal = Decimal("0.00")

    def cancel(self):
        self.status = "Cancelled"

    def updateStatus(self, status: str):
        self.status = status


def test_calculate_totals_basic():
    """Test that calculateTotals correctly computes subtotal, tax, and total for a simple order."""
    order = Order(
        orderId=1,
        status="Pending",
        items=[
            OrderItem(orderItemId=1, orderId=1, quantity=2, itemPrice="10.00"),
            OrderItem(orderItemId=2, orderId=1, quantity=1, itemPrice="3.50"),
        ],
        deliveryAddress="123 Main St",
        deliveryFee="2.00",
    )

    PricingService.calculateTotals(order)

    assert order.subtotal == Decimal("23.50")
    assert order.deliveryFee == Decimal("2.00")
    assert order.tax == Decimal("2.35")
    assert order.total == Decimal("27.85")


def test_calculate_totals_empty_order():
    order = Order(
        orderId=2,
        status="Pending",
        items=[],
        deliveryAddress="123 Main St",
        deliveryFee="4.99",
    )

    PricingService.calculateTotals(order)

    assert order.subtotal == Decimal("0.00")
    assert order.deliveryFee == Decimal("4.99")
    assert order.tax == Decimal("0.00")
    assert order.total == Decimal("4.99")


def test_calculate_totals_rounding_half_up():
    order = Order(
        orderId=3,
        status="Pending",
        items=[OrderItem(orderItemId=3, orderId=3, quantity=1, itemPrice="0.05")],
        deliveryAddress="123 Main St",
        deliveryFee="0.00",
    )

    PricingService.calculateTotals(order)

    assert order.subtotal == Decimal("0.05")
    assert order.tax == Decimal("0.01")
    assert order.total == Decimal("0.06")


def test_calculate_totals_negative_quantity_raises():
    order = Order(
        orderId=4,
        status="Pending",
        items=[OrderItem(orderItemId=4, orderId=4, quantity=-1, itemPrice="1.00")],
        deliveryAddress="123 Main St",
        deliveryFee="0.00",
    )

    with pytest.raises(ValueError, match="quantity"):
        PricingService.calculateTotals(order)


def test_calculate_totals_negative_price_raises():
    order = Order(
        orderId=5,
        status="Pending",
        items=[OrderItem(orderItemId=5, orderId=5, quantity=1, itemPrice="-1.00")],
        deliveryAddress="123 Main St",
        deliveryFee="0.00",
    )

    with pytest.raises(ValueError, match="price"):
        PricingService.calculateTotals(order)
