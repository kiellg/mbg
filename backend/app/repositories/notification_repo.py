"""Repository for notification records."""

from datetime import datetime, timezone
from typing import Dict

from backend.app.data.notification_data import NOTIFICATIONS


def create_notification(message: str, order_id: str) -> Dict[str, str]:
    """Create and store a notification record."""
    record = {
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "order_id": order_id,
    }
    NOTIFICATIONS.append(record)
    return record
