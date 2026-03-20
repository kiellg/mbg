"""Tests for restaurant sorting endpoints"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_sort_restaurants_desc():
    """Restaurants should be sorted by rating descending"""
    response = client.get("/restaurants/sorted?sort_by=rating&order=desc")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    ratings = [r["rating"] for r in data]

    assert ratings == sorted(ratings, reverse=True)

def test_sort_restaurants_asc():
    """Restaurants should be sorted by rating ascending"""

    response = client.get("/restaurants/sorted?sort_by=rating&order=asc")

    assert response.status_code == 200

    data = response.json()

    ratings = [r["rating"] for r in data]

    assert ratings == sorted(ratings)

def test_sort_restaurants_invalid_field():
    """Invalid sort field shouldn't break endpoint"""
    response = client.get("/restaurants/sorted?sort_by=unknown&order=desc")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

def test_sort_restaurants_invalid_order():
    """Invalid order should default to normal sorting"""
    response = client.get("/restaurants/sorted?sort_by=rating&order=invalid")

    assert response.status_code == 200

    data = response.json()

    ratings = [r["rating"] for r in data]

    assert ratings == sorted(ratings)

def test_paginated_sorted_restaurants_desc():
    """Paginated restaurants should be sorted by rating descending"""
    response = client.get(
        "/restaurants/paginated/sorted?page=1&limit=5&sort_by=rating&order=desc"
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data

    ratings = [r["rating"] for r in data["items"]]

    assert ratings == sorted(ratings, reverse=True)

def test_paginated_sorted_restaurants_limit():
    """Paginated limit should still apply with sorting"""
    response = client.get("/restaurants/paginated/sorted?page=1&limit=1&sort_by=rating&order=desc")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1

def test_menu_sorted_by_price_asc():
    """Menu items should be sorted by price ascending"""
    response = client.get(
        "/restaurants/1/menu/paginated/sorted?sort_by=price&order=asc"
    )

    assert response.status_code == 200

    data = response.json()

    items = data["items"]

    prices = [
        item["price_cents"]
        for item in items
        if item["price_cents"] is not None
    ]

    assert prices == sorted(prices)

def test_menu_sorted_by_price_desc():
    """Menu items should be sort by price descending"""
    response = client.get(
        "/restaurants/1/menu/paginated/sorted?sort_by=price&order=desc"
    )

    assert response.status_code == 200

    data = response.json()

    items = data["items"]

    prices = [
        item["price_cents"]
        for item in items
        if item["price_cents"] is not None
    ]

    assert prices == sorted(prices, reverse=True)

def test_menu_sort_handles_missing_prices():
    """Menu sorting should handle None price safely"""
    response = client.get(
        "/restaurants/1/menu/paginated/sorted?sort_by=price&order=asc"
    )

    assert response.status_code == 200

    data = response.json()

    items = data["items"]

    assert isinstance(items, list)
    assert len(items) > 0

def test_menu_sorted_invalid_field():
    """Invalid sort field shouldn't break menu endpoint"""
    response = client.get(
        "/restaurants/1/menu/paginated/sorted?sort_by=invalid&order=asc"
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert isinstance(data["items"], list)

def test_menu_sorted_restaurant_not_found():
    """Sorting menu should still return 404 for invalid restaurant"""
    response = client.get(
        "/restaurants/99999/menu/paginated/sorted?sort_by=price&order=asc"
    )

    assert response.status_code == 404
