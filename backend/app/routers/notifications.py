"""Router for notification endpoints."""

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.notification import NotificationResponse
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
def read_notifications(current_user=Depends(get_current_user)):
    """Return newest-first notifications for the current user."""
    return notification_service.list_notifications_for_user(current_user["user_id"])


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: str,
    current_user=Depends(get_current_user),
):
    """Mark a visible notification as read for the current user."""
    return notification_service.mark_notification_as_read_for_user(
        notification_id,
        current_user["user_id"],
    )
