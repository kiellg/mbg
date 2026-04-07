# pylint: disable=protected-access, duplicate-code
"""Unit tests for PricingService."""


from dataclasses import dataclass
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.services.pricing_service import PricingService


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
    coupon_snapshot: object = None
    subtotal: Decimal = Decimal("0.00")
    discount: Decimal = Decimal("0.00")
    discounted_subtotal: Decimal = Decimal("0.00")
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
    assert order.discount == Decimal("0.00")
    assert order.discounted_subtotal == Decimal("23.50")
    assert order.delivery_fee == Decimal("5.00")
    assert order.tax == Decimal("2.35")
    assert order.total == Decimal("30.85")


def test_calculate_tax_rounds_half_up():
    """Test tax calculation rounds half up to two decimal places."""
    assert PricingService.calculate_tax(Decimal("99.95"), Decimal("0.10")) == Decimal("10.00")


def test_calculate_totals_rounds_item_prices_before_storing_totals():
    """Test calculate_totals normalizes item prices and totals to two decimal places."""
    order = Order(
        order_id=2,
        status="Pending",
        items=[
            OrderItem(order_item_id=1, order_id=2, quantity=2, item_price="1.005"),
        ],
        delivery_address="123 Main St",
        delivery_method="walk",
    )

    PricingService.calculate_totals(order)

    assert order.subtotal == Decimal("2.02")
    assert order.delivery_fee == Decimal("5.00")
    assert order.tax == Decimal("0.20")
    assert order.total == Decimal("7.22")


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
    assert order.discount == Decimal("0.00")
    assert order.discounted_subtotal == Decimal("0.00")
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
    assert order.discount == Decimal("0.00")
    assert order.discounted_subtotal == Decimal("30.00")
    assert order.delivery_fee == Decimal("10.00")
    assert order.tax == Decimal("3.00")
    assert order.total == Decimal("43.00")


def test_calculate_totals_applies_percentage_discount_before_tax():
    """Test percentage discounts reduce subtotal before tax and total are computed."""
    order = Order(
        order_id=14,
        status="Pending",
        items=[OrderItem(order_item_id=1, order_id=14, quantity=1, item_price="49.99")],
        delivery_address="123 Main St",
        delivery_method="walk",
        coupon_snapshot={
            "code": "SAVE10",
            "discount_type": "percentage",
            "percent_off": 10,
            "amount_off_cents": None,
            "minimum_subtotal_cents": 0,
        },
    )

    PricingService.calculate_totals(order)

    assert order.subtotal == Decimal("49.99")
    assert order.discount == Decimal("5.00")
    assert order.discounted_subtotal == Decimal("44.99")
    assert order.tax == Decimal("4.50")
    assert order.delivery_fee == Decimal("5.00")
    assert order.total == Decimal("54.49")


def test_calculate_totals_caps_fixed_discount_at_subtotal():
    """Test fixed discounts are capped so the discounted subtotal never drops below zero."""
    order = Order(
        order_id=15,
        status="Pending",
        items=[OrderItem(order_item_id=1, order_id=15, quantity=1, item_price="4.00")],
        delivery_address="123 Main St",
        delivery_method="walk",
        coupon_snapshot={
            "code": "FREE100",
            "discount_type": "fixed_amount",
            "percent_off": None,
            "amount_off_cents": 1000,
            "minimum_subtotal_cents": 0,
        },
    )

    PricingService.calculate_totals(order)

    assert order.subtotal == Decimal("4.00")
    assert order.discount == Decimal("4.00")
    assert order.discounted_subtotal == Decimal("0.00")
    assert order.tax == Decimal("0.00")
    assert order.delivery_fee == Decimal("5.00")
    assert order.total == Decimal("5.00")


def test_calculate_totals_drops_discount_when_repriced_below_snapshot_minimum():
    """Test repricing keeps the order valid but drops the stored discount below minimum subtotal."""
    order = Order(
        order_id=16,
        status="Pending",
        items=[OrderItem(order_item_id=1, order_id=16, quantity=1, item_price="10.00")],
        delivery_address="123 Main St",
        delivery_method="walk",
        coupon_snapshot={
            "code": "MIN60",
            "discount_type": "percentage",
            "percent_off": 15,
            "amount_off_cents": None,
            "minimum_subtotal_cents": 6000,
        },
    )

    PricingService.calculate_totals(order)

    assert order.subtotal == Decimal("10.00")
    assert order.discount == Decimal("0.00")
    assert order.discounted_subtotal == Decimal("10.00")
    assert order.tax == Decimal("1.00")
    assert order.total == Decimal("16.00")


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
    with pytest.raises(HTTPException) as exc:
        PricingService._validate_order(None)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order is required"


def test_validate_order_rejects_missing_items():
    """Test that order validation rejects an order with missing items."""
    order = Order(
        order_id=5,
        status="Pending",
        items=None,
        delivery_address="123 Main St",
        delivery_method="walk",
    )

    with pytest.raises(HTTPException) as exc:
        PricingService._validate_order(order)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order items are required"


def test_validate_item_rejects_none_item():
    """Test that item validation rejects a missing order item."""
    with pytest.raises(HTTPException) as exc:
        PricingService._validate_item(None)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order item is required"


def test_validate_item_rejects_none_quantity():
    """Test that item validation rejects an item with a missing quantity."""
    item = OrderItem(order_item_id=1, order_id=6, quantity=None, item_price="10.00")

    with pytest.raises(HTTPException) as exc:
        PricingService._validate_item(item)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order item quantity is required"


def test_validate_item_rejects_zero_quantity():
    """Test that item validation rejects an item with zero quantity."""
    item = OrderItem(order_item_id=1, order_id=7, quantity=0, item_price="10.00")

    with pytest.raises(HTTPException) as exc:
        PricingService._validate_item(item)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order item quantity must be greater than zero"


def test_validate_item_rejects_negative_quantity():
    """Test that item validation rejects an item with a negative quantity."""
    item = OrderItem(order_item_id=1, order_id=8, quantity=-1, item_price="10.00")

    with pytest.raises(HTTPException) as exc:
        PricingService._validate_item(item)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order item quantity must be greater than zero"


def test_validate_item_rejects_none_item_price():
    """Test that item validation rejects an item with a missing price."""
    item = OrderItem(order_item_id=1, order_id=9, quantity=1, item_price=None)

    with pytest.raises(HTTPException) as exc:
        PricingService._validate_item(item)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order item price is required"


def test_validate_item_rejects_invalid_item_price():
    """Test that item validation rejects an item with a non-numeric price."""
    item = OrderItem(order_item_id=1, order_id=10, quantity=1, item_price="abc")

    with pytest.raises(HTTPException) as exc:
        PricingService._validate_item(item)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order item price must be a valid number"


def test_validate_item_rejects_negative_item_price():
    """Test that item validation rejects an item with a negative price."""
    item = OrderItem(order_item_id=1, order_id=11, quantity=1, item_price="-5.00")

    with pytest.raises(HTTPException) as exc:
        PricingService._validate_item(item)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Order item price cannot be negative"


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

    with pytest.raises(HTTPException) as exc:
        PricingService._validate_tax_rate(order)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Tax rate must be a valid number"


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

    with pytest.raises(HTTPException) as exc:
        PricingService._validate_tax_rate(order)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Tax rate cannot be negative"


def test_calculate_delivery_fee_rejects_invalid_delivery_method():
    """Test that delivery fee calculation rejects an unsupported delivery method."""
    with pytest.raises(HTTPException) as exc:
        PricingService.calculate_delivery_fee("plane")

    assert exc.value.status_code == 400
    assert exc.value.detail == "Delivery method must be one of: walk, bike, car"


def test_calculate_delivery_fee_rejects_missing_delivery_method():
    """Test that delivery fee calculation rejects a missing delivery method."""
    with pytest.raises(HTTPException) as exc:
        PricingService.calculate_delivery_fee(None)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Delivery method is required"
