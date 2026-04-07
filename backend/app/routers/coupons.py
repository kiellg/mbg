"""Router for admin coupon management endpoints."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, Request, status

from app.schemas.coupon import CouponCreateRequest, CouponResponse, CouponUpdateRequest
from app.services import coupon_service
from app.services.role_service import require_admin

router = APIRouter(prefix="/admin/coupons", tags=["admin-coupons"])


def get_session_token(
        request: Request,
        session_token: Optional[str] = Header(default=None),
) -> Optional[str]:
    """Return session token from header or cookie."""
    if session_token:
        return session_token

    return request.cookies.get("session_token")


def authenticate_admin(
        request: Request,
        session_token: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """Authenticate the user and ensure they are an admin."""
    token = get_session_token(request, session_token)
    return require_admin(token)


@router.post("", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(
    payload: CouponCreateRequest,
    request: Request,
    session_token: Optional[str] = Header(default=None),
):
    """Create a coupon that can later be applied at checkout."""
    authenticate_admin(request, session_token)
    return coupon_service.create_coupon(payload)


@router.get("", response_model=list[CouponResponse])
def list_all_coupons(
    request: Request,
    session_token: Optional[str] = Header(default=None),
):
    """List all coupons for admin management."""
    authenticate_admin(request, session_token)
    return coupon_service.list_coupons()


@router.get("/{coupon_code}", response_model=CouponResponse)
def get_coupon(
    coupon_code: str,
    request: Request,
    session_token: Optional[str] = Header(default=None),
):
    """Return a single coupon by its code."""
    authenticate_admin(request, session_token)
    return coupon_service.get_coupon(coupon_code)


@router.patch("/{coupon_code}", response_model=CouponResponse)
def update_coupon(
    coupon_code: str,
    payload: CouponUpdateRequest,
    request: Request,
    session_token: Optional[str] = Header(default=None),
):
    """Update coupon fields while keeping the code immutable."""
    authenticate_admin(request, session_token)
    return coupon_service.update_coupon(coupon_code, payload)


@router.patch("/{coupon_code}/deactivate", response_model=CouponResponse)
def deactivate_coupon(
    coupon_code: str,
    request: Request,
    session_token: Optional[str] = Header(default=None),
):
    """Deactivate a coupon without deleting its historical usage."""
    authenticate_admin(request, session_token)
    return coupon_service.deactivate_coupon(coupon_code)


@router.delete("/{coupon_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coupon(
    coupon_code: str,
    request: Request,
    session_token: Optional[str] = Header(default=None),
):
    """Delete a coupon from the live store."""
    authenticate_admin(request, session_token)
    coupon_service.delete_coupon(coupon_code)
