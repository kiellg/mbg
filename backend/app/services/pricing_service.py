"""Pricing service logic for order totals."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from backend.app.schemas.order import DeliveryMethod

TWOPLACES = Decimal("0.01")
DELIVERY_FEE_BY_METHOD = {
    DeliveryMethod.WALK: Decimal("5.00"),
    DeliveryMethod.BIKE: Decimal("8.00"),
    DeliveryMethod.CAR: Decimal("10.00"),
}


def _to_money(value: object) -> Decimal:
    """Convert a monetary value to the system standard of 2 decimal places."""
    return Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


class PricingService:  # pylint: disable=too-few-public-methods
    """Service for calculating order subtotal, tax, delivery fee, and total."""

    DEFAULT_TAX_RATE = Decimal("0.10")

    @staticmethod
    def calculate_tax(subtotal: Decimal, tax_rate: Decimal) -> Decimal:
        """Calculate tax for a subtotal at a given tax rate."""
        return (subtotal * tax_rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    @staticmethod
    def _validate_order(order) -> None:
        """Validate required order-level fields."""
        if order is None:
            raise ValueError("Order is required")

        if not hasattr(order, "items") or order.items is None:
            raise ValueError("Order items are required")

    @staticmethod
    def _validate_item(item) -> tuple[int, Decimal]:
        """Validate an order item and return quantity and decimal price."""
        if item is None:
            raise ValueError("Order item is required")

        if not hasattr(item, "quantity"):
            raise ValueError("Order item quantity is required")
        if not hasattr(item, "item_price"):
            raise ValueError("Order item price is required")

        quantity = item.quantity
        if quantity is None:
            raise ValueError("Order item quantity is required")
        if quantity <= 0:
            raise ValueError("Order item quantity must be greater than zero")

        price = item.item_price
        if price is None:
            raise ValueError("Order item price is required")

        try:
            price_decimal = Decimal(str(price))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValueError("Order item price must be a valid number") from exc

        if price_decimal < 0:
            raise ValueError("Order item price cannot be negative")

        return quantity, price_decimal

    @staticmethod
    def calculate_delivery_fee(delivery_method: str) -> Decimal:
        """Calculate fixed delivery fee based on delivery method."""
        method = getattr(delivery_method, "value", delivery_method)

        if method is None:
            raise ValueError("Delivery method is required")

        try:
            method_enum = DeliveryMethod(str(method).strip().lower())
        except ValueError as exc:
            raise ValueError("Delivery method must be one of: walk, bike, car") from exc

        return _to_money(DELIVERY_FEE_BY_METHOD[method_enum])

    @staticmethod
    def _validate_tax_rate(order) -> Decimal:
        """Validate and return tax rate as a Decimal."""
        tax_rate_raw = getattr(order, "tax_rate", PricingService.DEFAULT_TAX_RATE)
        try:
            tax_rate = Decimal(str(tax_rate_raw))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValueError("Tax rate must be a valid number") from exc

        if tax_rate < 0:
            raise ValueError("Tax rate cannot be negative")

        return tax_rate

    @staticmethod
    def calculate_totals(order) -> None:
        """Mutate order fields with recalculated subtotal, tax, delivery fee, and total."""
        PricingService._validate_order(order)

        subtotal = Decimal("0.00")
        for item in order.items:
            quantity, price_decimal = PricingService._validate_item(item)
            subtotal += _to_money(price_decimal) * Decimal(quantity)

        subtotal = _to_money(subtotal)
        delivery_method = getattr(order, "delivery_method", None)
        delivery_fee = PricingService.calculate_delivery_fee(delivery_method)
        tax_rate = PricingService._validate_tax_rate(order)

        tax = PricingService.calculate_tax(subtotal, tax_rate)
        total = _to_money(subtotal + delivery_fee + tax)

        order.subtotal = subtotal
        order.delivery_fee = delivery_fee
        order.tax = tax
        order.total = total
