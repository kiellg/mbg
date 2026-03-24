"""Integration tests for browsing, searching, and recently viewed"""

from fastapi.testclient import TestClient
from backend.main import app
from backend.app.data.recently_viewed_data import _RECENTLY_VIEWED

client = TestClient(app)

def setup_function():
    _RECENTLY_VIEWED.clear()

def login_user():
    """Helper to create and login user"""
    client.post("/auth/register", json={
        "name": "user1",
        "email": "user1@email.com",
        "password": "pass123",
        "role": "customer",
    })

    response = client.post("/auth/login", json={
        "email":"user1@email.com",
        "password": "pass123",
    })

    return response.cookies

def test_browse_restaurants_and_menu():
    """Browse restaurants and menus"""
    response = client.get("/restaurants")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    response = client.get("/restaurants/1/menu")
    assert response.status_code == 200
    assert "menu" in response.json()

def test_search_and_filter():
    "Search restaurants and menu items + filter"
    response = client.get("/restaurants/search?q=keg")
    assert response.status_code == 200

    response = client.get("/restaurants/filter?cuisine_types=Italian")
    assert response.status_code == 200

def test_pagination_limits_results():
    """Pagination actually limits results"""
    response = client.get("/restaurants/paginated?page=1&limit=1")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert len(data["items"]) <= 1

def test_sorting_order():
    """Sorting should be in correct order"""
    response = client.get("/restaurants/sorted?sort_by=rating&order=desc")
    assert response.status_code == 200

    data = response.json()
    ratings = [r["rating"] for r in data]

    assert ratings == sorted(ratings, reverse=True)

def test_menu_item_detail():
    """View detailed information for menu items"""
    response = client.get("/restaurants/1/menu/1")
    assert response.status_code == 200

    data = response.json()
    assert "name" in data

def test_search_suggestions():
    """Provide search suggestions"""
    response = client.get("/restaurants/search/suggestions?q=burger")
    assert response.status_code == 200

    data = response.json()
    assert "suggestions" in data

def test_recently_viewed_flow():
    """Login -> view -> tracked in recently viewed"""
    cookies = login_user()

    # Initially empty
    response = client.get("/recently-viewed", cookies=cookies)
    assert response.status_code == 200
    assert response.json()["items"] == []

    # View restaurant
    client.get("/restaurants/1/menu", cookies=cookies)

    # View menu item
    client.get("/restaurants/1/menu/1", cookies=cookies)

    # Now it should contain items
    response = client.get("/recently-viewed", cookies=cookies)
    data = response.json()

    assert "items" in data
    assert len(data["items"]) >= 1

def test_recently_viewed_no_login():
    """Should return empty when not logged in"""
    response = client.get("/recently-viewed", cookies={})

    assert response.status_code == 200
    assert response.json()["items"] == []
