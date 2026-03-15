"""Tests for restaurant service layer service validation"""
# pylint: disable=duplicate-code

from unittest.mock import patch

from backend.app.services.restaurants_service import (
    get_all_restaurants_list,
    create_new_restaurant,
    update_restaurant_by_id,
    add_menu_item,
    update_menu_item_by_id,
)
from backend.app.schemas.restaurant import (
    RestaurantCreate, RestaurantUpdate,
    MenuItemCreate, MenuItemUpdate,
)

BASE_RECORD = {
    "id": 1,
    "name": "Test Bistro",
    "address": "123 Main St",
    "rating": 4,
    "opening_hours": "9am-9pm",
    "owner_id": "42",
    "menu": [],
}

CREATED_ITEM = {
    "id": 1, 
    "restaurant_id": 1, 
    "name": "Pizza", 
    "price_cents": 999,
    "description": "", 
    "dietary_tag": "", 
    "is_visible": True, "is_active": True, "is_available": True, 
    "category": {"id": 1, "name": ""},
}

ITEM_CREATE = MenuItemCreate(
    name="Pizza",
    price_cents=999,
    description="",
    dietary_tag="",
    is_visible=True, is_active=True, is_available=True,
    category_id=1,
)

SERVICE = "backend.app.services.restaurants_service"

def test_get_all_restaurants_returns_all():
    """Test that all restaurants are returned from the service"""
    records = [BASE_RECORD, {**BASE_RECORD, "id": 2, "name": "Pizza Place"}]
    with patch(f"{SERVICE}.get_all_restaurants", return_value=records):
        result = get_all_restaurants_list()
    assert len(result) == 2

def test_get_all_restaurants_empty():
    """Test that an empty list is returned when no restaurants exist"""
    with patch(f"{SERVICE}.get_all_restaurants", return_value=[]):
        result = get_all_restaurants_list()
    assert not result

def test_create_new_restaurant_calls_repo_correctly():
    """Test that create_new_restaurant calls the repo with the correct parameters"""
    body = RestaurantCreate(name="New Place", address="456 Elm St", opening_hours="8am-10pm")
    with patch(f"{SERVICE}.create_restaurant",
               return_value={**BASE_RECORD, "name": "New Place"}) as mock:
        result = create_new_restaurant(body, owner_id="10")
    mock.assert_called_once_with(
        name="New Place", address="456 Elm St",
        rating=None, opening_hours="8am-10pm", owner_id="10",
    )
    assert result["name"] == "New Place"

def test_update_restaurant_success():
    """Test that update_restaurant_by_id successfully updates and returns the restaurant"""
    updated = {**BASE_RECORD, "name": "Updated Bistro"}
    with patch(f"{SERVICE}.get_restaurant_record", return_value=BASE_RECORD), \
         patch(f"{SERVICE}.repo_update_restaurant", return_value=updated) as mock:
        result = update_restaurant_by_id(1, RestaurantUpdate(name="Updated Bistro"))
    mock.assert_called_once_with(1, {"name": "Updated Bistro"})
    assert result["name"] == "Updated Bistro"

def test_add_menu_item_delegates_to_repo():
    """Test that add_menu_item calls the repository function with the correct parameters"""
    with patch(f"{SERVICE}.get_restaurant_record", return_value=BASE_RECORD), \
         patch(f"{SERVICE}.repo_add_menu_item", return_value=CREATED_ITEM) as mock:
        result = add_menu_item(1, ITEM_CREATE)
    mock.assert_called_once_with(1, ITEM_CREATE.model_dump())
    assert result["restaurant_id"] == 1

def test_update_menu_item_success():
    """Test that update_menu_item_by_id successfully updates and returns the menu item"""
    updated = {**CREATED_ITEM, "name": "Updated Pizza"}
    with patch(f"{SERVICE}.get_restaurant_record", return_value=BASE_RECORD), \
         patch(f"{SERVICE}.repo_update_menu_item", return_value=updated) as mock:
        result = update_menu_item_by_id(1, 1, MenuItemUpdate(name="Updated Pizza"))
    mock.assert_called_once_with(1, 1, {"name": "Updated Pizza"})
    assert result["name"] == "Updated Pizza"
