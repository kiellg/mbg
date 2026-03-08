"""Pricing service logic for order totals."""

from decimal import Decimal, ROUND_HALF_UP

TWOPLACES = Decimal("0.01")


def _to_money(value: object) -> Decimal:
    """Convert a monetary value to the system standard of 2 decimal places."""
    return Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


class PricingService:  # pylint: disable=too-few-public-methods
    """Service for calculating order subtotal, tax, and total."""

    DEFAULT_TAX_RATE = Decimal("0.10")

    @staticmethod
    def calculate_totals(order) -> None:
        """Mutate order fields with recalculated monetary totals using consistent 2-dp rounding."""
        subtotal = Decimal("0.00")

        for item in order.items:
            quantity = item.quantity
            price = item.item_price

            if quantity < 0:
                raise ValueError("Order item quantity cannot be negative")
            if Decimal(str(price)) < 0:
                raise ValueError("Order item price cannot be negative")

            line_total = (_to_money(price) * Decimal(quantity)).quantize(
                TWOPLACES, rounding=ROUND_HALF_UP
            )
            subtotal += line_total

        subtotal = _to_money(subtotal)
        delivery_fee = _to_money(getattr(order, "delivery_fee", 0))
        tax_rate = Decimal(str(getattr(order, "tax_rate", PricingService.DEFAULT_TAX_RATE)))
        tax = _to_money(subtotal * tax_rate)
        total = _to_money(subtotal + delivery_fee + tax)

        order.subtotal = subtotal
        order.delivery_fee = delivery_fee
        order.tax = tax
        order.total = total
