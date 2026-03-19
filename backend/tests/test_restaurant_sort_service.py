"""Tests for restaurant sorting in service layer"""

from backend.app.services.restaurants_service import get_all_restaurants_list
from backend.app.data.restaurants_data import _DB

def test_restaurants_sorted_by_rating_desc():
    """Restaurants should be sorted by rating descending"""
    results = get_all_restaurants_list("rating", "desc")

    ratings = [r.rating for r in results]

    assert ratings == sorted(ratings, reverse=True)

def test_restaurants_sorted_by_rating_asc():
    """Restaurants should be sorted by rating ascending"""
    results = get_all_restaurants_list("rating", "asc")

    ratings = [r.rating for r in results]

    assert ratings == sorted(ratings)

def test_restaurants_sorting_stable_for_equal_ratings():
    """Restaurants with the same rating should keep their original order after sorting"""
    original = []
    for r in _DB.values():
        original.append((r["id"], r["rating"]))
        r["rating"] = 5

    results = get_all_restaurants_list("rating", "desc")

    ids = [r.id for r in results]

    expected_ids = list(_DB.keys())

    assert ids == expected_ids

    for rid, rating in original:
        _DB[rid]["rating"] = rating

def test_restaurants_invalid_sort_field_returns_unsorted():
    """Invalid sort field shouldn't crash and return original order"""
    results = get_all_restaurants_list("invalid_field", "desc")

    ids = [r.id for r in results]
    expected_ids = list(_DB.keys())

    assert ids == expected_ids
