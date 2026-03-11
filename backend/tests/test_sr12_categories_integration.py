"""Tests for category and dietary tag integration in restaurant menu endpoints"""

from fastapi.testclient import TestClient
from backend.main import app
from backend.app.data.categories_data import VALID_CATEGORIES, VALID_DIETARY_TAGS

client = TestClient(app)

MANAGER_SESSION = {"user_id": 10, "role": "manager"}
MANAGER_TOKEN = "valid-manager-token"

BASE_RESTAURANT = {
    "id": 1,
    "name": "Test Bistro",
    "address": "123 Main St",
    "rating": 4,
    "opening_hours": "9am-9pm",
    "owner_id": 42,
    "menu": [],
}

SERVICE = "backend.app.services.restaurants_service"
ROUTER = "backend.app.routers.restaurants"

def auth_headers(token=MANAGER_TOKEN):
    """Helper to create auth headers for requests"""
    return {"session_token": token}

def test_list_categories_success():
    """Test that categories endpoint returns all valid categories and dietary tags"""
    response = client.get("/restaurants/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "dietary_tags" in data

def test_list_categories_contains_all_predefined():
    """Test that all predefined categories are present in response"""
    response = client.get("/restaurants/categories")
    returned_ids = {c["id"] for c in response.json()["categories"]}
    assert returned_ids == set(VALID_CATEGORIES.keys())

def test_list_categories_contains_all_dietary_tags():
    """Test that all predefined dietary tags are present in response"""
    response = client.get("/restaurants/categories")
    returned_tags = set(response.json()["dietary_tags"])
    assert returned_tags == VALID_DIETARY_TAGS
