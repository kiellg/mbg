"""Unit tests for delivery schemas"""
from unittest.mock import patch
import pytest
from pydantic import ValidationError
from backend.app.schemas.delivery import DeliveryStatusResponse, DeliveryDetailsResponse
from backend.app.schemas.order import OrderStatus, DeliveryMethod
from backend.app.repositories import order_repo

@patch("backend.app.data.order_data._ORDERDB", {})

def test_delivery_status_response_valid():
    """Valid input should create a DeliveryStatusResponse successfully"""
    response = DeliveryStatusResponse(
        order_id="abc1234",
        status=OrderStatus.PENDING,
        delivery_time="30 mins",
        delivery_time_actual=28.5,
        delivery_delay=1.5,
    )
    assert response.order_id == "abc1234"
    assert response.status == OrderStatus.PENDING
    assert response.delivery_time_actual == 28.5
    assert response.delivery_delay == 1.5

def test_delivery_status_response_invalid_status():
    """Invalid order status should raise a ValidationError"""
    with pytest.raises(ValidationError):
        DeliveryStatusResponse(
            order_id="abc1234",
            status="parachute",
            delivery_time="30 mins",
            delivery_time_actual=28.5,
            delivery_delay=1.5,
        )

def test_delivery_details_response_valid():
    """Valid input should create a DeliveryDetailsResponse successfully"""
    response = DeliveryDetailsResponse(
        order_id="abc1234",
        driver_name="John Doe",
        delivery_method=DeliveryMethod.BIKE,
        delivery_distance=3.5,
        route_taken="Main St -> Oak Ave",
    )
    assert response.driver_name == "John Doe"
    assert response.delivery_method == DeliveryMethod.BIKE
    assert response.delivery_distance == 3.5

def test_delivery_details_response_invalid_method():
    """Invalid delivery method should raise a ValidationError"""
    with pytest.raises(ValidationError):
        DeliveryDetailsResponse(
            order_id="abc1234",
            driver_name="John Doe",
            delivery_method="parachute",
            delivery_distance=3.5,
            route_taken="Main St -> Oak Ave",
        )

def test_create_order_record_stores_delivery_fields():
    """create_order_record should initialize all SR28 delivery fields"""
    order = order_repo.create_order_record(
        customer_id="CUST-001",
        restaurant_id=1,
        delivery_address="123 Test St",
        items=[{"quantity": 1, "item_price": "10.00"}],
    )
    assert order["delivery_time"] == ""
    assert order["delivery_time_actual"] == 0.0
    assert order["delivery_delay"] == 0.0
    assert order["delivery_distance"] == 0.0
    assert order["driver_name"] == ""
    assert order["route_taken"] == ""
