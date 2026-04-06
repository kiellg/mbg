"""Tests for scheduled order feature"""

from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from main import app
from app.data import order_data

client = TestClient(app)

def setup_function():
    """Reset order data before each test"""
    order_data._ORDERDB.clear()

def _base_payload():
    """Helper to generate a valid order payload"""
    return {
        "customer_id": "1",
        "restaurant_id": 1,
        "delivery_address": "123 Main St",
        "delivery_method": "walk",
        "status": "Pending",
        "items": [
            {
                "quantity": 1,
                "item_price": "10.00",
            }
        ],
    }

def test_create_scheduled_order_success():
    """Creating an order with future scheduled_time should succeed"""
    future_time = datetime.utcnow() + timedelta(hours=1)

    payload = _base_payload()
    payload["scheduled_time"] = future_time.isoformat()

    response = client.post("/orders", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["is_scheduled"] is True
    assert data["scheduled_time"] is not True

def test_create_scheduled_order_in_past_fails():
    """Creating an order with past scheduled_time should return 400"""
    past_time = datetime.utcnow() - timedelta(hours=1)

    payload = _base_payload()
    payload["scheduled_time"] = past_time.isoformat()

    response = client.post("/orders", json=payload)

    assert response.status_code == 400
    assert "Scheduled time must be in the future" in response.text

def test_create_regular_order_not_scheduled():
    """Creating an order without scheduled_time should not be scheduled"""
    payload = _base_payload()

    response = client.post("/orders", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["is_scheduled"] is False
    assert data["scheduled_time"] is None

def test_scheduled_order_becomes_Active_after_time():
    """Scheduled order should become active after scheduled_time passes"""
    future_time = datetime.utcnow() + timedelta(seconds=1)

    payload = _base_payload()
    payload["scheduled_time"] = future_time.isoformat()

    response = client.post("/orders", json=payload)
    assert response.status_code == 200

    data = response.json()
    order_id = data["order_id"]

    assert data["is_scheduled"] is True

    # wait until scheduled time passes
    import time
    time.sleep(2)

    # trigger processing
    response = client.get("/orders")
    assert response.status_code == 200

    orders = response.json()

    # find our order
    updated_order = next(o for o in orders if o["order_id"] == order_id)

    assert updated_order["is_scheduled"] is False
    assert updated_order["status"] == "Pending"

def test_scheduled_order_not_activated_early():
    """Scheduled order should remain scheduled before its time"""
    future_time = datetime.utcnow() + timedelta(minutes=5)

    payload = _base_payload()
    payload["scheduled_time"] = future_time.isoformat()

    response = client.post("/orders", json=payload)
    assert response.status_code == 200

    data = response.json()
    order_id = data["order_id"]

    # immediately fetch orders
    response = client.get("/orders")
    assert response.status_code == 200

    orders = response.json()
    order = next(o for o in orders if o["order_id"] == order_id)

    assert order["is_scheduled"] is True
