"""Service layer for admin user profile management"""
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from app.repositories import user_repo
from app.schemas.user import ProfileResponse
from app.repositories import order_repo, restaurant_repo, session_repo

def list_all_profiles() -> list[dict]:
    """Return all user profiles with resolved roles"""
    raw_profiles = user_repo.list_all_profiles()
    return [
        ProfileResponse.model_validate(p).model_dump()
        for p in raw_profiles
    ]

def delete_user(user_id: str) -> None:
    """Delete a user by ID, revoking sessions and cleaning up cross-entity references"""
    if user_repo.is_admin(user_id):
        raise HTTPException(
            status_code=403,
            detail="Admin accounts cannot be deleted.",
        )
    deleted = user_repo.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found.")

    session_repo.delete_sessions_for_user(user_id)
    restaurant_repo.clear_owner_reference(user_id)
    order_repo.clear_driver_reference(user_id)

def get_order_analytics() -> dict:
    """Return analytics on orders, including totals and breakdowns by
    status and time periods"""
    now = datetime.now(timezone.utc)
    today = now.date()
    week_ago = today - timedelta(days=7)

    orders_today = 0
    orders_this_week = 0
    orders_by_status = {}

    for order in order_repo.list_order_records():
        created = order["created_at"].date()
        status = order["status"]

        if created == today:
            orders_today += 1
        if created >= week_ago:
            orders_this_week += 1

        orders_by_status[status] = orders_by_status.get(status, 0) + 1

    return {
        "total_orders": sum(orders_by_status.values()),
        "orders_today": orders_today,
        "orders_this_week": orders_this_week,
        "orders_by_status": orders_by_status,
    }
