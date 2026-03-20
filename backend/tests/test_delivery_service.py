"""Unit tests for delivery_service.py"""
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from backend.app.data.notification_data import NOTIFICATIONS
from backend.app.services import delivery_service
from backend.app.schemas.order import OrderStatus, DeliveryMethod

FAKE_ORDER = {
    "order_id": "abc1234",
    "status": "Pending",
    "delivery_time": "30 mins",
    "delivery_time_actual": 28.5,
    "delivery_delay": 1.5,
    "driver_name": "John Doe",
    "delivery_method": "bike",
    "delivery_distance": 3.5,
    "route_taken": "Main St -> Oak Ave",
}


def setup_function():
    """Reset notification state before each test."""
    NOTIFICATIONS.clear()

@patch("backend.app.services.delivery_service.order_repo")
def test_get_delivery_status_valid(mock_order_repo):
    """get_delivery_status should return correct fields for a valid order"""
    mock_order_repo.get_order_record.return_value = FAKE_ORDER

    result = delivery_service.get_delivery_status("abc1234")

    assert result.order_id == "abc1234"
    assert result.status == OrderStatus.PENDING
    assert result.delivery_time == "30 mins"
    assert result.delivery_time_actual == 28.5
    assert result.delivery_delay == 1.5

@patch("backend.app.services.delivery_service.order_repo")
def test_get_delivery_status_not_found(mock_order_repo):
    """get_delivery_status should raise 404 if order does not exist"""
    mock_order_repo.get_order_record.return_value = None

    with pytest.raises(HTTPException) as exc:
        delivery_service.get_delivery_status("nonexistent")

    assert exc.value.status_code == 404

@patch("backend.app.services.delivery_service.order_repo")
def test_get_delivery_details_valid(mock_order_repo):
    """get_delivery_details should return correct driver name and method"""
    mock_order_repo.get_order_record.return_value = FAKE_ORDER

    result = delivery_service.get_delivery_details("abc1234")

    assert result.driver_name == "John Doe"
    assert result.delivery_method == DeliveryMethod.BIKE
    assert result.delivery_distance == 3.5
    assert result.route_taken == "Main St -> Oak Ave"

@patch("backend.app.services.delivery_service.order_repo")
def test_get_delivery_details_not_found(mock_order_repo):
    """get_delivery_details should raise 404 if order does not exist"""
    mock_order_repo.get_order_record.return_value = None

    with pytest.raises(HTTPException) as exc:
        delivery_service.get_delivery_details("nonexistent")

    assert exc.value.status_code == 404

@patch("backend.app.services.delivery_service.order_repo")
@patch("backend.app.services.delivery_service.restaurant_repo")
def test_get_kitchen_queue_returns_cooking_orders(mock_restaurant_repo, mock_order_repo):
    """Should return only Cooking orders for the given restaurant."""
    mock_restaurant_repo.get_restaurant_record.return_value = {
        "id": 1, "owner_id": "josemou"
        }
    mock_order_repo.list_order_records.return_value = [
        {**FAKE_ORDER, "status": "Cooking", "restaurant_id": 1,
         "order_id": "order1", "customer_id": "cust1",
         "delivery_address": "123 Test St", "items": [],
         "subtotal": "0.00", "tax": "0.00",
         "delivery_fee": "0.00", "total": "0.00"},
         {**FAKE_ORDER, "status": "Pending", "restaurant_id": 1,
          "order_id": "order2", "customer_id": "cust1",
          "delivery_address": "123 Test St", "items": [],
          "subtotal": "0.00", "tax": "0.00",
          "delivery_fee": "0.00", "total": "0.00"},
          ]
    result = delivery_service.get_kitchen_queue(restaurant_id=1, manager_id="josemou")
    assert len(result) == 1
    assert result[0].status.value == "Cooking"

@patch("backend.app.services.delivery_service.order_repo")
@patch("backend.app.services.delivery_service.restaurant_repo")
def test_get_kitchen_queue_returns_empty_when_no_cooking_orders(mock_restaurant_repo,
                                                                mock_order_repo ):
    """Should return empty list when no Cooking orders exist for the restaurant."""
    mock_restaurant_repo.get_restaurant_record.return_value = {
        "id": 1, "owner_id": "josemou"
        }
    mock_order_repo.list_order_records.return_value = []
    result = delivery_service.get_kitchen_queue(restaurant_id=1, manager_id="josemou")
    assert result == []

@patch("backend.app.services.delivery_service.restaurant_repo")
def test_get_kitchen_queue_raises_404_if_restaurant_not_found(mock_restaurant_repo):
    """Should raise 404 when restaurant does not exist."""
    mock_restaurant_repo.get_restaurant_record.return_value = None
    with pytest.raises(HTTPException) as exc:
        delivery_service.get_kitchen_queue(restaurant_id=420, manager_id="josemou")
    assert exc.value.status_code == 404

@patch("backend.app.services.delivery_service.restaurant_repo")
def test_get_kitchen_queue_raises_403_if_wrong_manager(mock_restaurant_repo):
    """Should raise 403 when manager does not own the restaurant."""
    mock_restaurant_repo.get_restaurant_record.return_value = {"id": 1, "owner_id": "pepguar"}
    with pytest.raises(HTTPException) as exc:
        delivery_service.get_kitchen_queue(restaurant_id=1, manager_id="josemou")
    assert exc.value.status_code == 403

@patch("backend.app.services.delivery_service.notification_service")
@patch("backend.app.services.delivery_service.order_repo")
def test_update_delivery_status_creates_notification_for_valid_transition(
    mock_order_repo,
    mock_notification_service,
):
    """Valid delivery status updates should create a notification."""
    mock_order_repo.get_order_record.return_value = FAKE_ORDER
    mock_order_repo.set_order_status.return_value = {**FAKE_ORDER, "status": "Cooking"}

    result = delivery_service.update_delivery_status("abc1234", "Cooking")

    assert result["status"] == "Cooking"
    mock_order_repo.set_order_status.assert_called_once_with("abc1234", "Cooking")
    mock_notification_service.create_order_status_changed_notification.assert_called_once_with(
        "abc1234",
        "Cooking",
    )


@patch("backend.app.services.delivery_service.notification_service")
@patch("backend.app.services.delivery_service.order_repo")
def test_update_delivery_status_invalid_transition_does_not_create_notification(
    mock_order_repo,
    mock_notification_service,
):
    """Invalid delivery transitions should not create a notification."""
    mock_order_repo.get_order_record.return_value = {
        **FAKE_ORDER,
        "status": "Delivered",
    }

    with pytest.raises(HTTPException) as exc:
        delivery_service.update_delivery_status("abc1234", "Pending")

    assert exc.value.status_code == 400
    mock_order_repo.set_order_status.assert_not_called()
    mock_notification_service.create_order_status_changed_notification.assert_not_called()
