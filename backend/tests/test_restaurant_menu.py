"""Tests for the restaurant menu endpoint"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_restaurant_menu_prices_and_fields():
    r = client.get("/restaurants/1/menu")
    data = r.json()

    burger = next(i for i in data["menu"] if i["id"] == 1)
    assert burger["price_status"] == "ok"
    assert burger["display_price"].startswith("$")
    assert len(burger["display_price"]) > 1

def test_hidden_item_has_no_display_price():
    r = client.get("/restaurants/1/menu")
    data = r.json()

    item = next(i for i in data["menu"] if i["id"] == 2)
    assert item["display_price"] is None

def test_visible_negative_price_is_flagged():
    r = client.get("/restaurants/1/menu")
    data = r.json()

    item = next(i for i in data["menu"] if i["id"] == 3)
    assert item["price_status"] == "invalid"
    assert item["display_price"] is None

def test_visible_missing_price_is_flagged():
    r = client.get("/restaurants/1/menu")
    data = r.json()

    item = next(i for i in data["menu"] if i["id"] == 4)
    assert item["price_status"] == "missing"
    assert item["display_price"] is None