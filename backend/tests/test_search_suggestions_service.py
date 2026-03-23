"""Tests for search suggestions service"""

from backend.app.services.restaurants_service import get_search_suggestions

def test_empty_query_returns_empty():
    """Empty query should return no suggestions"""
    result = get_search_suggestions("")
    assert result.suggestions == []

def test_no_match_returns_empty():
    """Query with no matches should return empty list"""
    result = get_search_suggestions("not_found")
    assert result.suggestions == []

def test_restaurant_suggestion_present():
    """Should include restaurant suggestions"""
    result = get_search_suggestions("keg")

    assert any(
        s.suggestion_type == "restaurant"
        and "keg" in s.name.lower()
        for s in result.suggestions
    )

def test_menu_item_suggestion_present():
    """Should include menu item suggestions"""
    result = get_search_suggestions("steak")

    assert any(
        s.suggestion_type == "menu_item"
        and "steak" in s.name.lower()
        for s in result.suggestions
    )

def test_menu_item_has_restaurant_id():
    """Menu item suggestions should include restaurant_id"""
    result = get_search_suggestions("steak")

    menu_items = [s for s in result.suggestions if s.suggestion_type == "menu_item"]

    assert all(s.restaurant_id is not None for s in menu_items)

def test_restaurant_has_no_restaurant_id():
    """Restaurant suggestions should mot include restaurant_id"""
    result = get_search_suggestions("keg")

    restaurants = [s for s in result.suggestions if s.suggestion_type == "restaurant"]

    assert all(s.restaurant_id is None for s in restaurants)

def test_case_insensitive_search():
    """Search should be case insensitive"""
    result_lower = get_search_suggestions("keg")
    result_upper = get_search_suggestions("KEG")

    assert result_lower.suggestions == result_upper.suggestions
