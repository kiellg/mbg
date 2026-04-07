"""Router tests for admin coupon management endpoints."""

from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

BASE_COUPON = {
    "code": "SAVE20",
    "discount_type": "percentage",
    "percent_off": 20,
    "amount_off_cents": None,
    "minimum_subtotal_cents": 0,
    "expires_at": "2099-12-31T23:59:59Z",
    "is_active": True,
}


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.create_coupon")
def test_create_coupon_returns_201(mock_create_coupon, mock_authenticate_admin):
    """Admin coupon create route should return the created coupon."""
    mock_authenticate_admin.return_value = {"user_id": "admin-1"}
    mock_create_coupon.return_value = BASE_COUPON

    response = client.post(
        "/admin/coupons",
        json={
            "code": "save20",
            "discount_type": "percentage",
            "percent_off": 20,
        },
    )

    assert response.status_code == 201
    assert response.json()["code"] == "SAVE20"


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.list_coupons")
def test_list_coupons_returns_200(mock_list_coupons, mock_authenticate_admin):
    """Admin coupon list route should return all coupons."""
    mock_authenticate_admin.return_value = {"user_id": "admin-1"}
    mock_list_coupons.return_value = [BASE_COUPON]

    response = client.get("/admin/coupons")

    assert response.status_code == 200
    assert response.json() == [BASE_COUPON]


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.get_coupon")
def test_get_coupon_returns_200(mock_get_coupon, mock_authenticate_admin):
    """Admin coupon get route should return one coupon by code."""
    mock_authenticate_admin.return_value = {"user_id": "admin-1"}
    mock_get_coupon.return_value = BASE_COUPON

    response = client.get("/admin/coupons/save20")

    assert response.status_code == 200
    assert response.json()["code"] == "SAVE20"


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.update_coupon")
def test_update_coupon_returns_200(mock_update_coupon, mock_authenticate_admin):
    """Admin coupon update route should return the updated coupon."""
    mock_authenticate_admin.return_value = {"user_id": "admin-1"}
    mock_update_coupon.return_value = {**BASE_COUPON, "percent_off": 25}

    response = client.patch(
        "/admin/coupons/save20",
        json={"percent_off": 25},
    )

    assert response.status_code == 200
    assert response.json()["percent_off"] == 25


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.deactivate_coupon")
def test_deactivate_coupon_returns_200(mock_deactivate_coupon, mock_authenticate_admin):
    """Admin coupon deactivate route should return the deactivated coupon."""
    mock_authenticate_admin.return_value = {"user_id": "admin-1"}
    mock_deactivate_coupon.return_value = {**BASE_COUPON, "is_active": False}

    response = client.patch("/admin/coupons/save20/deactivate")

    assert response.status_code == 200
    assert response.json()["is_active"] is False


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.delete_coupon")
def test_delete_coupon_returns_204(mock_delete_coupon, mock_authenticate_admin):
    """Admin coupon delete route should return no content."""
    mock_authenticate_admin.return_value = {"user_id": "admin-1"}
    mock_delete_coupon.return_value = None

    response = client.delete("/admin/coupons/save20")

    assert response.status_code == 204
    assert response.content == b""


@patch("app.routers.coupons.authenticate_admin")
def test_create_coupon_returns_403_for_non_admin(mock_authenticate_admin):
    """Admin coupon routes should reject non-admin access."""
    mock_authenticate_admin.side_effect = HTTPException(status_code=403, detail="Access denied")

    response = client.post(
        "/admin/coupons",
        json={
            "code": "save20",
            "discount_type": "percentage",
            "percent_off": 20,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"
