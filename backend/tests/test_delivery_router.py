"""Integration tests for delivery router endpoints"""
# pylint: disable=duplicate-code, unused-argument, unused-import
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app
from fastapi import HTTPException

client = TestClient(app)

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
def test_get_delivery_status_returns_200(mock_order_repo):
    """GET /{order_id}/status should return 200 with correct status and ETA fields"""
    mock_order_repo.get_order_record.return_value = FAKE_ORDER

    response = client.get("/orders/abc1234/status")

    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "abc1234"
    assert data["status"] == "Pending"
    assert data["delivery_time"] == "30 mins"
    assert data["delivery_time_actual"] == 28.5
    assert data["delivery_delay"] == 1.5

@patch("backend.app.services.delivery_service.order_repo")
def test_get_delivery_status_reflects_updated_status(mock_order_repo):
    """GET /{order_id}/status should reflect updated status after a status change"""
    mock_order_repo.get_order_record.return_value = {
        **FAKE_ORDER,
        "status": "Cooking",
    }

    response = client.get("/orders/abc1234/status")

    assert response.status_code == 200
    assert response.json()["status"] == "Cooking"

@patch("backend.app.services.delivery_service.order_repo")
def test_get_delivery_status_not_found(mock_order_repo):
    """GET /{order_id}/status should return 404 for a non-existent order"""
    mock_order_repo.get_order_record.return_value = None

    response = client.get("/orders/nonexistent/status")

    assert response.status_code == 404

@patch("backend.app.services.delivery_service.order_repo")
def test_get_delivery_details_returns_200(mock_order_repo):
    """GET /{order_id}/details should return 200 with driver name and delivery method"""
    mock_order_repo.get_order_record.return_value = FAKE_ORDER

    response = client.get("/orders/abc1234/details")

    assert response.status_code == 200
    data = response.json()
    assert data["driver_name"] == "John Doe"
    assert data["delivery_method"] == "bike"
    assert data["delivery_distance"] == 3.5

@patch("backend.app.services.delivery_service.order_repo")
def test_get_delivery_details_not_found(mock_order_repo):
    """GET /{order_id}/details should return 404 for a non-existent order"""
    mock_order_repo.get_order_record.return_value = None

    response = client.get("/orders/nonexistent/details")

    assert response.status_code == 404

@patch("backend.app.services.delivery_service.order_repo")
@patch("backend.app.routers.deliveries.require_driver")
def test_driver_update_status_valid_transition(mock_require_driver, mock_order_repo):
    """Driver should be able to update status through valid transitions"""
    mock_order_repo.get_order_record.return_value = FAKE_ORDER
    mock_order_repo.set_order_status.return_value = {
        **FAKE_ORDER,
        "status": "Cooking"
    }

    response = client.patch(
        "/orders/abc1234/status",
        json={"status": "Cooking"},
        headers={"session-token": "valid-driver-token"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Cooking"


@patch("backend.app.routers.deliveries.require_driver")
def test_driver_update_status_no_token(mock_require_driver):
    """PATCH /{order_id}/status should return 403 if no valid driver session token"""
    mock_require_driver.side_effect = HTTPException(status_code=403, detail="Forbidden")

    response = client.patch(
        "/orders/abc1234/status",
        json={"status": "Cooking"},
    )

    assert response.status_code == 403


@patch("backend.app.services.delivery_service.order_repo")
@patch("backend.app.routers.deliveries.require_driver")
def test_driver_update_status_order_not_found(mock_require_driver, mock_order_repo):
    """PATCH /{order_id}/status should return 404 if order does not exist"""
    mock_order_repo.get_order_record.return_value = None

    response = client.patch(
        "/orders/nonexistent/status",
        json={"status": "Cooking"},
        headers={"session-token": "valid-driver-token"},
    )

    assert response.status_code == 404

@patch("backend.app.services.delivery_service.order_repo")
@patch("backend.app.routers.deliveries.require_driver")
def test_driver_invalid_status_transition(mock_require_driver, mock_order_repo):
    """PATCH /{order_id}/status should reject invalid status transitions"""
    mock_require_driver.return_value = None
    mock_order_repo.get_order_record.return_value = {
        **FAKE_ORDER,
        "status": "Delivered",
    }

    response = client.patch(
        "/orders/abc1234/status",
        json={"status": "Pending"},
        headers={"session-token": "valid-driver-token"},
    )

    assert response.status_code == 400
