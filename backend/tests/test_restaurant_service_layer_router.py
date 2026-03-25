"""Tests for restaurant service layer router validation"""

from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

MANAGER_SESSION = {"user_id": 10, "role": "manager"}
MANAGER_TOKEN = "valid-manager-token"

BASE_RESTAURANT = {
    "id": 2,
    "name": "Test Bistro2",
    "address": "123 Main St2",
    "rating": 2,
    "opening_hours": "9am-10pm",
    "owner_id": "41",
    "menu": [],
}

BASE_ITEM = {
    "id": 1,
    "restaurant_id": 1,
    "name": "Burger",
    "price_cents": 1299,
    "description": "Tasty",
    "dietary_tag": "",
    "is_visible": True, "is_active": True, "is_available": True,
    "category": {"id": 1, "name": ""},
}

NEW_ITEM_PAYLOAD = {
    "name": "Caesar Salad",
    "price_cents": 899,
    "description": "Fresh romaine",
    "dietary_tag": "vegetarian",
    "is_visible": True, "is_active": True, "is_available": True,
    "category_id": 1,
}

def auth_headers(token=MANAGER_TOKEN):
    """Helper function to generate auth headers for testing"""
    return {"session_token": token}

SERVICE = "app.services.restaurants_service"
ROUTER = "app.routers.restaurants"

def test_list_restaurants_success():
    """Test that the restaurant list endpoint returns all restaurants"""
    with patch(f"{SERVICE}.get_all_restaurants", return_value=[BASE_RESTAURANT]):
        response = client.get("/restaurants")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Test Bistro2"

def test_list_restaurants_empty():
    """Test that the restaurant list endpoint returns an empty list"""
    with patch(f"{SERVICE}.get_all_restaurants", return_value=[]):
        response = client.get("/restaurants")
    assert response.status_code == 200
    assert response.json() == []

def test_create_restaurant_success():
    """Test that creating a restaurant successfully returns the created restaurant"""
    payload = {"name": "New Bistro", "address": "789 Oak Ave", "opening_hours": "9am-9pm"}
    with patch(f"{ROUTER}.require_manager", return_value=MANAGER_SESSION), \
         patch(f"{SERVICE}.create_restaurant",
               return_value={**BASE_RESTAURANT, "name": "New Bistro"}):
        response = client.post("/restaurants", json=payload, headers=auth_headers())
    assert response.status_code == 201

def test_create_restaurant_no_token():
    """Test that creating a restaurant without a token returns 401"""
    payload = {"name": "New Bistro", "address": "789 Oak Ave", "opening_hours": "9am-9pm"}
    response = client.post("/restaurants", json=payload)
    assert response.status_code == 401

def test_patch_restaurant_success():
    """Test that patching a restaurant successfully updates and returns the restaurant"""
    updated = {**BASE_RESTAURANT, "name": "Updated Bistro"}
    with patch(f"{ROUTER}.require_manager", return_value=MANAGER_SESSION), \
         patch(f"{SERVICE}.get_restaurant_record", return_value=BASE_RESTAURANT), \
         patch(f"{SERVICE}.repo_update_restaurant", return_value=updated):
        response = client.patch("/restaurants/1", json={"name": "Updated Bistro"},
                                headers=auth_headers())
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Bistro"

def test_patch_restaurant_not_found():
    """Test that patching a non-existent restaurant returns 404"""
    with patch(f"{ROUTER}.require_manager", return_value=MANAGER_SESSION), \
         patch(f"{SERVICE}.get_restaurant_record", return_value=None):
        response = client.patch("/restaurants/999", json={"name": "X"}, headers=auth_headers())
    assert response.status_code == 404

def test_patch_restaurant_no_token():
    """Test that patching a restaurant without a token returns 401"""
    response = client.patch("/restaurants/1", json={"name": "X"})
    assert response.status_code == 401

def test_patch_menu_item_success():
    """Test that patching a menu item successfully updates and returns the item"""
    updated = {**BASE_ITEM, "name": "Updated Burger"}
    with patch(f"{ROUTER}.require_manager", return_value=MANAGER_SESSION), \
         patch(f"{SERVICE}.get_restaurant_record", return_value=BASE_RESTAURANT), \
         patch(f"{SERVICE}.repo_update_menu_item", return_value=updated):
        response = client.patch("/restaurants/1/menu/1", json={"name": "Updated Burger"},
                                headers=auth_headers())
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Burger"

def test_patch_menu_item_not_found():
    """Test that patching a non-existent menu item returns 404"""
    with patch(f"{ROUTER}.require_manager", return_value=MANAGER_SESSION), \
         patch(f"{SERVICE}.get_restaurant_record",
               return_value=BASE_RESTAURANT), \
         patch(f"{SERVICE}.repo_update_menu_item", return_value=None):
        response = client.patch("/restaurants/1/menu/99", json={"name": "X"},
                                headers=auth_headers())
    assert response.status_code == 404

def test_patch_menu_item_no_token():
    """Test that patching a menu item without a token returns 401"""
    response = client.patch("/restaurants/1/menu/1", json={"name": "X"})
    assert response.status_code == 401
