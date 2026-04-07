#pylint: disable=unused-argument
"""Unit tests for favourite_service.py"""
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.services import favourite_service

USER_ID = "user-001"
RESTAURANT_TARGET_ID = "1"
MENU_ITEM_TARGET_ID = "2"
RESTAURANT_ID = 1

MOCK_USER = {"user_id": USER_ID, "name": "Test User"}
MOCK_RESTAURANT = {"id": 1, "name": "Test Restaurant", "menu": []}
MOCK_MENU_ITEM = {"id": 2, "name": "Burger", "price_cents": 1000}
MOCK_FAVOURITE = {
    "favourite_id": "fav-001",
    "user_id": USER_ID,
    "target_id": RESTAURANT_TARGET_ID,
    "target_type": "restaurant",
}

SERVICE = "app.services.favourite_service"
PATCH_GET_USER = f"{SERVICE}.get_user_by_id"
PATCH_GET_RESTAURANT = f"{SERVICE}.get_restaurant_record"
PATCH_GET_MENU_ITEM = f"{SERVICE}.get_menu_item"
PATCH_IS_FAVOURITE = f"{SERVICE}.is_favourite"
PATCH_ADD_FAVOURITE = f"{SERVICE}.add_favourite"
PATCH_REMOVE_FAVOURITE = f"{SERVICE}.remove_favourite"

@patch(PATCH_ADD_FAVOURITE)
@patch(PATCH_IS_FAVOURITE)
@patch(PATCH_GET_RESTAURANT)
@patch(PATCH_GET_USER)
def test_add_favourite_restaurant_success(
    mock_get_user, mock_get_restaurant, mock_is_favourite, mock_add
):
    """Test adding a restaurant to favourites successfully"""
    mock_get_user.return_value = MOCK_USER
    mock_get_restaurant.return_value = MOCK_RESTAURANT
    mock_is_favourite.return_value = False
    mock_add.return_value = MOCK_FAVOURITE

    result = favourite_service.add_favourite_for_user(
        USER_ID, RESTAURANT_TARGET_ID, "restaurant"
    )
    assert result.target_id == RESTAURANT_TARGET_ID
    assert result.target_type == "restaurant"

@patch(PATCH_ADD_FAVOURITE)
@patch(PATCH_IS_FAVOURITE)
@patch(PATCH_GET_MENU_ITEM)
@patch(PATCH_GET_USER)
def test_add_favourite_menu_item_success(
    mock_get_user, mock_get_menu_item, mock_is_favourite, mock_add
):
    """Test adding a menu item to favourites successfully"""
    mock_get_user.return_value = MOCK_USER
    mock_get_menu_item.return_value = MOCK_MENU_ITEM
    mock_is_favourite.return_value = False
    mock_add.return_value = {
        "favourite_id": "fav-002",
        "user_id": USER_ID,
        "target_id": MENU_ITEM_TARGET_ID,
        "target_type": "menu_item",
    }

    result = favourite_service.add_favourite_for_user(
        USER_ID, MENU_ITEM_TARGET_ID, "menu_item", restaurant_id=RESTAURANT_ID
    )
    assert result.target_type == "menu_item"
    mock_get_menu_item.assert_called_once_with(RESTAURANT_ID, int(MENU_ITEM_TARGET_ID))

@patch(PATCH_GET_RESTAURANT)
@patch(PATCH_GET_USER)
def test_add_favourite_raises_404_if_restaurant_not_found(
    mock_get_user, mock_get_restaurant
):
    """Test that adding a non-existent restaurant to favourites raises 404"""
    mock_get_user.return_value = MOCK_USER
    mock_get_restaurant.return_value = None

    with pytest.raises(HTTPException) as exc:
        favourite_service.add_favourite_for_user(
            USER_ID, RESTAURANT_TARGET_ID, "restaurant"
        )
    assert exc.value.status_code == 404

@patch(PATCH_GET_MENU_ITEM)
@patch(PATCH_GET_USER)
def test_add_favourite_raises_404_if_menu_item_not_found(
    mock_get_user, mock_get_menu_item
):
    """Test that adding a non-existent menu item to favourites raises 404"""
    mock_get_user.return_value = MOCK_USER
    mock_get_menu_item.return_value = None

    with pytest.raises(HTTPException) as exc:
        favourite_service.add_favourite_for_user(
            USER_ID, MENU_ITEM_TARGET_ID, "menu_item", restaurant_id=RESTAURANT_ID
        )
    assert exc.value.status_code == 404

@patch(PATCH_REMOVE_FAVOURITE)
@patch(PATCH_IS_FAVOURITE)
def test_remove_favourite_success(mock_is_favourite, mock_remove):
    """Test removing a favourite successfully"""
    mock_is_favourite.return_value = True

    result = favourite_service.remove_favourite_for_user(USER_ID, RESTAURANT_TARGET_ID,
                                                         "restaurant")
    assert result["detail"] == "Favourite removed successfully"

@patch(PATCH_IS_FAVOURITE)
def test_remove_favourite_raises_404_if_not_found(mock_is_favourite):
    """Test that trying to remove a non-existent favourite raises 404"""
    mock_is_favourite.return_value = False

    with pytest.raises(HTTPException) as exc:
        favourite_service.remove_favourite_for_user(USER_ID, RESTAURANT_TARGET_ID,
                                                    "restaurant")
    assert exc.value.status_code == 404
