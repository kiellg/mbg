"""Router tests for admin coupon management endpoints."""

from unittest.mock import ANY, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.schemas.coupon import CouponCreateRequest, CouponUpdateRequest
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
    mock_authenticate_admin.assert_called_once_with(ANY, None)
    mock_create_coupon.assert_called_once()
    payload = mock_create_coupon.call_args.args[0]
    assert isinstance(payload, CouponCreateRequest)
    assert payload.code == "save20"
    assert payload.discount_type.value == "percentage"
    assert payload.percent_off == 20


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.list_coupons")
def test_list_coupons_returns_200(mock_list_coupons, mock_authenticate_admin):
    """Admin coupon list route should return all coupons."""
    mock_authenticate_admin.return_value = {"user_id": "admin-1"}
    mock_list_coupons.return_value = [BASE_COUPON]

    response = client.get("/admin/coupons")

    assert response.status_code == 200
    assert response.json() == [BASE_COUPON]
    mock_authenticate_admin.assert_called_once_with(ANY, None)
    mock_list_coupons.assert_called_once_with()


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.get_coupon")
def test_get_coupon_returns_200(mock_get_coupon, mock_authenticate_admin):
    """Admin coupon get route should return one coupon by code."""
    mock_authenticate_admin.return_value = {"user_id": "admin-1"}
    mock_get_coupon.return_value = BASE_COUPON

    response = client.get("/admin/coupons/save20")

    assert response.status_code == 200
    assert response.json()["code"] == "SAVE20"
    mock_authenticate_admin.assert_called_once_with(ANY, None)
    mock_get_coupon.assert_called_once_with("save20")


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
    mock_authenticate_admin.assert_called_once_with(ANY, None)
    mock_update_coupon.assert_called_once()
    coupon_code, payload = mock_update_coupon.call_args.args
    assert coupon_code == "save20"
    assert isinstance(payload, CouponUpdateRequest)
    assert payload.percent_off == 25


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.deactivate_coupon")
def test_deactivate_coupon_returns_200(mock_deactivate_coupon, mock_authenticate_admin):
    """Admin coupon deactivate route should return the deactivated coupon."""
    mock_authenticate_admin.return_value = {"user_id": "admin-1"}
    mock_deactivate_coupon.return_value = {**BASE_COUPON, "is_active": False}

    response = client.patch("/admin/coupons/save20/deactivate")

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    mock_authenticate_admin.assert_called_once_with(ANY, None)
    mock_deactivate_coupon.assert_called_once_with("save20")


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.delete_coupon")
def test_delete_coupon_returns_204(mock_delete_coupon, mock_authenticate_admin):
    """Admin coupon delete route should return no content."""
    mock_authenticate_admin.return_value = {"user_id": "admin-1"}
    mock_delete_coupon.return_value = None

    response = client.delete("/admin/coupons/save20")

    assert response.status_code == 204
    assert response.content == b""
    mock_authenticate_admin.assert_called_once_with(ANY, None)
    mock_delete_coupon.assert_called_once_with("save20")


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.create_coupon")
def test_create_coupon_returns_422_for_invalid_request_body(
    mock_create_coupon,
    mock_authenticate_admin,
):
    """Admin coupon create route should reject invalid request bodies."""
    response = client.post(
        "/admin/coupons",
        json={
            "code": "save20",
            "discount_type": "percentage",
        },
    )

    assert response.status_code == 422
    mock_authenticate_admin.assert_not_called()
    mock_create_coupon.assert_not_called()


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.update_coupon")
def test_update_coupon_returns_422_for_invalid_request_body(
    mock_update_coupon,
    mock_authenticate_admin,
):
    """Admin coupon update route should reject invalid request bodies."""
    response = client.patch(
        "/admin/coupons/save20",
        json={"minimum_subtotal_cents": -1},
    )

    assert response.status_code == 422
    mock_authenticate_admin.assert_not_called()
    mock_update_coupon.assert_not_called()


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.update_coupon")
def test_update_coupon_returns_404_for_missing_coupon(
    mock_update_coupon,
    mock_authenticate_admin,
):
    """Admin coupon update route should return 404 when the coupon is missing."""
    mock_authenticate_admin.return_value = {"user_id": "admin-1"}
    mock_update_coupon.side_effect = HTTPException(status_code=404, detail="Coupon not found.")

    response = client.patch(
        "/admin/coupons/missing",
        json={"percent_off": 25},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Coupon not found."
    mock_authenticate_admin.assert_called_once_with(ANY, None)
    mock_update_coupon.assert_called_once()


@patch("app.routers.coupons.authenticate_admin")
@patch("app.routers.coupons.coupon_service.delete_coupon")
def test_delete_coupon_returns_404_for_missing_coupon(
    mock_delete_coupon,
    mock_authenticate_admin,
):
    """Admin coupon delete route should return 404 when the coupon is missing."""
    mock_authenticate_admin.return_value = {"user_id": "admin-1"}
    mock_delete_coupon.side_effect = HTTPException(status_code=404, detail="Coupon not found.")

    response = client.delete("/admin/coupons/missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "Coupon not found."
    mock_authenticate_admin.assert_called_once_with(ANY, None)
    mock_delete_coupon.assert_called_once_with("missing")


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
    mock_authenticate_admin.assert_called_once_with(ANY, None)
