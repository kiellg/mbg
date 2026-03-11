"""Shared utility functions for formatting values for display."""

def format_cad_from_cents(price_cents: int) -> str:
    """Convert price in cents to a formatted CAD string"""
    return f"${price_cents / 100:.2f}"