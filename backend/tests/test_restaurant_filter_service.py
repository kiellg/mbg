"""Tests for filtering services"""

from app.services.restaurants_service import(
    filter_restaurants,
    filter_menu_items_service,
)
from app.repositories.restaurant_repo import reset_restaurants

def setup_function():
    """Reset restaurant data before each test"""
    reset_restaurants()

def test_filter_restaurants_returns_list():
    """Restaurant filtering returns list"""
    results = filter_restaurants(["italian"])
    assert isinstance(results, list)

def test_filter_menu_items_returns_list():
    """Menu filtering returns list"""
    results = filter_menu_items_service(
        restaurant_id=1,
        categories=None,
        dietary_tags=None,
        min_price=None,
        max_price=None,
    )

    assert isinstance(results, list)

def test_filter_restaurants_returns_correct_cuisine():
    """Filtered restaurants should match the requested cuisine type"""
    results = filter_restaurants(["italian"])

    for r in results:
        assert r["cuisine_type"] == "italian"
