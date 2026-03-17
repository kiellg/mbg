"""Repository for notification records."""

from datetime import datetime, timezone
from typing import Dict, List

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


def list_notification_records() -> List[Dict[str, str]]:
    """Return notification records in newest-first order."""
    return list(reversed(NOTIFICATIONS))
