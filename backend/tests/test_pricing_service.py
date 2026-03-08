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
    delivery_method: object = "walk"
    subtotal: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    tax_rate: object = Decimal("0.10")
    delivery_fee: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")


def test_calculate_totals_walk_delivery_fee():
    """Test that walk delivery method applies the fixed 5.00 delivery fee."""
    order = Order(
        order_id=1,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=1, quantity=1, item_price="10.00"),
        ],
        delivery_address="123 Main St",
        delivery_method="walk",
    )

    PricingService.calculate_totals(order)

    assert order.delivery_fee == Decimal("5.00")


def test_calculate_totals_bike_delivery_fee():
    """Test that bike delivery method applies the fixed 8.00 delivery fee."""
    order = Order(
        order_id=2,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=2, quantity=1, item_price="10.00"),
        ],
        delivery_address="123 Main St",
        delivery_method="bike",
    )

    PricingService.calculate_totals(order)

    assert order.delivery_fee == Decimal("8.00")


def test_calculate_totals_car_delivery_fee():
    """Test that car delivery method applies the fixed 10.00 delivery fee."""
    order = Order(
        order_id=3,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=3, quantity=1, item_price="10.00"),
        ],
        delivery_address="123 Main St",
        delivery_method="car",
    )

    PricingService.calculate_totals(order)

    assert order.delivery_fee == Decimal("10.00")


def test_calculate_totals_includes_delivery_fee_in_total():
    """Test total calculation includes subtotal, tax, and fixed delivery fee."""
    order = Order(
        order_id=4,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=4, quantity=2, item_price="10.00"),
        ],
        delivery_address="123 Main St",
        delivery_method="bike",
    )

    PricingService.calculate_totals(order)

    assert order.subtotal == Decimal("20.00")
    assert order.tax == Decimal("2.00")
    assert order.delivery_fee == Decimal("8.00")
    assert order.total == Decimal("30.00")


def test_calculate_totals_rejects_invalid_delivery_method():
    """Test that calculate_totals rejects an unsupported delivery method."""
    order = Order(
        order_id=5,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=5, quantity=1, item_price="10.00"),
        ],
        delivery_address="123 Main St",
        delivery_method="drone",
    )

    with pytest.raises(ValueError, match="Delivery method must be one of: walk, bike, car"):
        PricingService.calculate_totals(order)
