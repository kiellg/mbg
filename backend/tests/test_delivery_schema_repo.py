"""Unit tests for delivery schemas"""
import pytest
from pydantic import ValidationError
from app.schemas.delivery import DeliveryStatusResponse, DeliveryDetailsResponse
from app.schemas.order import OrderStatus, DeliveryMethod
from app.repositories import order_repo

VALID_ORDER_ID = "abc1234"
VALID_DELIVERY_TIME = "30 mins"
VALID_DISTANCE = 3.5
VALID_ROUTE = "Main St -> Oak Ave"

def test_delivery_status_response_valid():
    """Valid input should create a DeliveryStatusResponse successfully"""
    response = DeliveryStatusResponse(
        order_id=VALID_ORDER_ID,
        status=OrderStatus.PENDING,
        delivery_time=VALID_DELIVERY_TIME,
        delivery_time_actual=28.5,
        delivery_delay=1.5,
    )
    assert response.order_id == VALID_ORDER_ID
    assert response.status == OrderStatus.PENDING
    assert response.delivery_time_actual == 28.5
    assert response.delivery_delay == 1.5

@pytest.mark.parametrize("invalid_status", ["parachute", "", "PENDING", "unknown"])
def test_delivery_status_response_invalid_status(invalid_status):
    """Invalid order status should raise a ValidationError"""
    with pytest.raises(ValidationError):
        DeliveryStatusResponse(
            order_id=VALID_ORDER_ID,
            status=invalid_status,
            delivery_time=VALID_DELIVERY_TIME,
            delivery_time_actual=28.5,
            delivery_delay=1.5,
        )

def test_delivery_details_response_valid():
    """Valid input should create a DeliveryDetailsResponse successfully"""
    response = DeliveryDetailsResponse(
        order_id=VALID_ORDER_ID,
        driver_name="John Doe",
        driver_id="driver-123",
        delivery_method=DeliveryMethod.BIKE,
        delivery_distance=VALID_DISTANCE,
        route_taken=VALID_ROUTE,
    )
    assert response.driver_name == "John Doe"
    assert response.driver_id == "driver-123"
    assert response.delivery_method == DeliveryMethod.BIKE
    assert response.delivery_distance == VALID_DISTANCE

@pytest.mark.parametrize("invalid_method", ["parachute", "", "BIKE", "unknown"])
def test_delivery_details_response_invalid_method(invalid_method):
    """Invalid delivery method should raise a ValidationError"""
    with pytest.raises(ValidationError):
        DeliveryDetailsResponse(
            order_id=VALID_ORDER_ID,
            driver_id="driver-123",
            driver_name="John Doe",
            delivery_method=invalid_method,
            delivery_distance=VALID_DISTANCE,
            route_taken=VALID_ROUTE,
        )

def test_create_order_record_stores_delivery_fields():
    """create_order_record should initialize all delivery fields with correct defaults"""
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
