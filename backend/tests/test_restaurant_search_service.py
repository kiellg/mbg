"""Tests for restaurant search service"""

from backend.app.services.restaurants_service import(
    search_restaurant,
    search_menu_items,
)
from backend.app.repositories.restaurant_repo import reset_restaurants

def setup_function():
    """Reset DB before each test"""
    reset_restaurants()

def test_search_restaurant_by_name():
    """Searching restaurants should return partial matches"""
    results = search_restaurant("keg")

    assert len(results) == 1
    assert results[0].name == "The Keg Steakhouse"

def test_search_menu_item_by_name():
    """Searching menu items should return matching items"""
    results = search_menu_items("roll")

    names = [r.name for r in results]

    assert "California Roll" in names
    assert "Spicy Tuna Roll" in names

def test_search_no_results():
    """Search should return empty list when nothing matches"""
    results = search_restaurant("pizza")

    assert results == []
