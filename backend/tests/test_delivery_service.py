"""Unit tests for delivery_service.py"""
import pytest
from unittest.mock import patch
from fastapi import HTTPException
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
