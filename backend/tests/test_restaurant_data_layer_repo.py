"""Tests for restaurant data layer repo validation"""

from backend.app.repositories.restaurant_repo import (
    get_restaurant_record,
    get_all_restaurants,
    create_restaurant,
    update_restaurant,
    delete_restaurant,
    add_menu_item,
    update_menu_item,
    delete_menu_item,
    get_active_menu_items,
    reset_restaurants,
)

def setup_function():
    """Reset DB before each test"""
    reset_restaurants()

def test_get_restaurant_record_returns_existing():
    """Should return record for existing restaurant"""
    record = get_restaurant_record(1)
    assert record is not None
    assert record["name"] == "The Keg Steakhouse"

def test_get_restaurant_record_returns_none_for_missing():
    """Should return None for nonexistent restaurant"""
    assert get_restaurant_record(999) is None

def test_get_all_restaurants_returns_all():
    """Should return all restaurants"""
    result = get_all_restaurants()
    assert isinstance(result, list)
    assert len(result) == 2

def test_create_restaurant_stores_record():
    """Should create and store a new restaurant"""
    r = create_restaurant(
        name="Burger Place",
        address="456 Main St",
        rating=3,
        opening_hours="Mon-Fri 10:00-20:00",
        owner_id=99,
    )
    assert r["id"] == 3
    assert r["name"] == "Burger Place"
    assert r["owner_id"] == 99
    assert not r["menu"]

def test_update_restaurant_changes_fields():
    """Should update only provided fields"""
    updated = update_restaurant(1, {"name": "The Keg Updated", "rating": 5})
    assert updated["name"] == "The Keg Updated"
    assert updated["rating"] == 5
    assert updated["address"] == "67 Bernard Ave, Kelowna, BC"

def test_delete_restaurant_removes_record():
    """Should remove restaurant and return True"""
    result = delete_restaurant(1)
    assert result is True
    assert get_restaurant_record(1) is None

def test_add_menu_item_appends_to_menu():
    """Should add a new item to the restaurant menu"""
    item = add_menu_item(1, {
        "name": "Lobster",
        "price_cents": 5999,
        "description": "Fresh lobster",
        "dietary_tag": "",
        "is_visible": True,
        "is_active": True,
        "is_available": True,
        "category": {"id": 10, "name": "Mains"},
    })
    assert item["restaurant_id"] == 1
    assert item["name"] == "Lobster"
    assert item["id"] == 5

def test_update_menu_item_changes_fields():
    """Should update only provided fields"""
    updated = update_menu_item(1, 1, {"price_cents": 5999, "name": "Ribeye Deluxe"})
    assert updated["price_cents"] == 5999
    assert updated["name"] == "Ribeye Deluxe"
    assert updated["description"] == "12oz AAA ribeye with garlic mashed potatoes"

def test_delete_menu_item_removes_item():
    """Should remove item from menu and return True"""
    result = delete_menu_item(1, 1)
    assert result is True
    record = get_restaurant_record(1)
    assert all(i["id"] != 1 for i in record["menu"])

def test_get_active_menu_items_returns_only_active():
    """Should return only items where is_active is True"""
    items = get_active_menu_items(1)
    assert all(i["is_active"] for i in items)
