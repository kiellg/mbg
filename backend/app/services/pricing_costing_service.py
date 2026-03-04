"""Pricing and costing service logic for order totals."""

from decimal import Decimal, ROUND_HALF_UP

TWOPLACES = Decimal("0.01")

def _to_money(value: object) -> Decimal:
    """Convert a value to a 2-decimal Decimal using half-up rounding."""
    return Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

class PricingService:
    """Service for calculating order subtotal, tax, and total."""

    DEFAULT_TAX_RATE = Decimal("0.10")

    @staticmethod
    def calculate_totals(order) -> None:
        """Mutate order fields with recalculated totals."""
        subtotal = Decimal("0.00")

        for item in order.items:
            quantity = item.quantity
            price = item.item_price

            if quantity < 0:
                raise ValueError("Order item quantity cannot be negative")
            if Decimal(str(price)) < 0:
                raise ValueError("Order item price cannot be negative")

            line_total = _to_money(price) * Decimal(quantity)
            subtotal += line_total

        subtotal = subtotal.quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        delivery_fee = _to_money(getattr(order, "delivery_fee", 0))
        tax_rate = Decimal(str(getattr(order, "tax_rate", PricingService.DEFAULT_TAX_RATE)))
        tax = (subtotal * tax_rate).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        total = (subtotal + delivery_fee + tax).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

        order.subtotal = subtotal
        order.delivery_fee = delivery_fee
        order.tax = tax
        order.total = total
