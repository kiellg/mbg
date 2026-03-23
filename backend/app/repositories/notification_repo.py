"""Repository for notification records."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import shortuuid

from backend.app.data.notification_data import NOTIFICATIONS


def _alloc_notification_id() -> str:
    """Allocate and return the next notification_id."""
    return shortuuid.ShortUUID().random(length=7)


def create_notification(message: str, order_id: str) -> Dict[str, Any]:
    """Create and store a notification record."""
    record = {
        "notification_id": _alloc_notification_id(),
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "order_id": order_id,
        "read_by_user_ids": [],
    }
    NOTIFICATIONS.append(record)
    return record


def get_notification_record(notification_id: str) -> Optional[Dict[str, Any]]:
    """Return a notification record by its notification_id."""
    return next(
        (
            record
            for record in NOTIFICATIONS
            if record.get("notification_id") == notification_id
        ),
        None,
    )


def mark_notification_as_read(notification_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Mark a notification as read for a specific user."""
    record = get_notification_record(notification_id)
    if record is None:
        return None

    read_by_user_ids = record.setdefault("read_by_user_ids", [])
    if user_id not in read_by_user_ids:
        read_by_user_ids.append(user_id)

    return record


def list_notification_records() -> List[Dict[str, Any]]:
    """Return notification records in newest-first order."""
    return list(reversed(NOTIFICATIONS))
