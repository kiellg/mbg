from fastapi import HTTPException

from backend.app.schemas.restaurant import RestaurantOut
from backend.app.schemas.menu import PriceStatus
from backend.app.data.restaurants_data import get_restaurant_record

def format_cad_from_cents(price_cents: int) -> str:
    return f"${price_cents / 100:.2f}"

def get_restaurant_menu(restaurant_id: int) -> RestaurantOut:
    record = get_restaurant_record(restaurant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    for item in record.get("menu", []):
        visible = item.get("is_visible", True)
        active = item.get("is_active", True)
        cents = item.get("price_cents", None)

        if not (visible and active):
            item["display_price"] = None
            item["price_status"] = PriceStatus.ok
            continue

        if cents is None:
            item["display_price"] = None
            item["price_status"] = PriceStatus.missing
        elif cents < 0:
            item["display_price"] = None
            item["price_status"] = PriceStatus.invalid
        else:
            item["display_price"] = format_cad_from_cents(cents)
            item["price_status"] = PriceStatus.ok

    return RestaurantOut(**record)
