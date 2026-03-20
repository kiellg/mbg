"""Router for notification endpoints."""

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_current_user
from backend.app.schemas.notification import NotificationResponse
from backend.app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
def read_notifications(current_user=Depends(get_current_user)):
    """Return newest-first notifications for the current user."""
    return notification_service.list_notifications_for_user(current_user["user_id"])
