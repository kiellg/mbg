"""Service layer for restaurant-related business logic"""

from fastapi import HTTPException

from backend.app.schemas.restaurant import RestaurantOut
from backend.app.schemas.menu import PriceStatus
from backend.app.data.restaurants_data import get_restaurant_record

def format_cad_from_cents(price_cents: int) -> str:
    """Convert price in cents to a formatted CAD string"""
    return f"${price_cents / 100:.2f}"

def get_restaurant_menu(restaurant_id: int) -> RestaurantOut:
    """Fetch restaurant data and process menu items for display"""
    record = get_restaurant_record(restaurant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    for item in record.get("menu", []):
        item["restaurant_id"] = restaurant_id

        visible = item.get("is_visible", True)
        active = item.get("is_active", True)
        cents = item.get("price_cents", None)

        if not (visible and active):
            item["display_price"] = None
            item["price_status"] = PriceStatus.OK
            continue

        if cents is None:
            item["display_price"] = None
            item["price_status"] = PriceStatus.MISSING
        elif cents < 0:
            item["display_price"] = None
            item["price_status"] = PriceStatus.INVALID
        else:
            item["display_price"] = format_cad_from_cents(cents)
            item["price_status"] = PriceStatus.OK

    return RestaurantOut(**record)
