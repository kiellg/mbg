"""Integration tests for /favourites endpoints"""
from fastapi.testclient import TestClient
from app.data.favourite_data import FAVOURITES
from app.repositories import user_repo, restaurant_repo
from app.dependencies import get_current_user
from main import app

client = TestClient(app)

def _register_and_login() -> dict:
    """Helper function to register a new user and return their record"""
    user = user_repo.create_user("testuser", "test@test.com", "pw123")
    return user

def _set_current_user(user_id: str):
    """Helper function to override the get_current_user dependency for testing"""
    app.dependency_overrides[get_current_user] = lambda: {"user_id": user_id}

def setup_function():
    """Reset the favourites data and dependency overrides before each test"""
    FAVOURITES.clear()
    app.dependency_overrides = {}

def test_add_favourite_restaurant_returns_201():
    """Test adding a restaurant to favourites returns 201 and correct response body"""
    user = _register_and_login()
    _set_current_user(user["user_id"])
    restaurant = restaurant_repo.get_restaurant_record(1)
    restaurant_id = str(restaurant["id"])

    response = client.post(
        "/favourites",
        json={"target_id": restaurant_id, "target_type": "restaurant"},
    )
    assert response.status_code == 201
    assert response.json()["target_id"] == restaurant_id
    assert response.json()["target_type"] == "restaurant"

def test_add_duplicate_favourite_returns_409():
    """Test that adding the same restaurant to favourites twice returns 409"""
    user = _register_and_login()
    _set_current_user(user["user_id"])
    restaurant = restaurant_repo.get_restaurant_record(1)
    restaurant_id = str(restaurant["id"])

    client.post(
        "/favourites",
        json={"target_id": restaurant_id, "target_type": "restaurant"},
    )
    response = client.post(
        "/favourites",
        json={"target_id": restaurant_id, "target_type": "restaurant"},
    )
    assert response.status_code == 409

def test_remove_favourite_returns_200():
    """Test that removing a favourite returns 200 and success message"""
    user = _register_and_login()
    _set_current_user(user["user_id"])
    restaurant = restaurant_repo.get_restaurant_record(1)
    restaurant_id = str(restaurant["id"])

    client.post(
        "/favourites",
        json={"target_id": restaurant_id, "target_type": "restaurant"},
    )
    response = client.delete(f"/favourites/{restaurant_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Favourite removed successfully"

def test_remove_nonexistent_favourite_returns_404():
    """Test that trying to remove a non-existent favourite returns 404"""
    user = _register_and_login()
    _set_current_user(user["user_id"])

    response = client.delete("/favourites/nonexistent-id")
    assert response.status_code == 404

def test_list_favourites_returns_only_current_users_favourites():
    """Test that listing favourites only returns records for the currently logged-in user"""
    user_a = _register_and_login()
    user_b = user_repo.create_user("other", "other@test.com", "pw123")
    restaurant = restaurant_repo.get_restaurant_record(1)
    restaurant_id = str(restaurant["id"])

    _set_current_user(user_a["user_id"])
    client.post(
        "/favourites",
        json={"target_id": restaurant_id, "target_type": "restaurant"},
    )

    _set_current_user(user_b["user_id"])
    response = client.get("/favourites")
    assert response.status_code == 200
    assert response.json() == []
