"""Repository functions for payment records"""

#pylint: disable=protected-access

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import shortuuid

from backend.app.data import payment_data

def _alloc_payment_id() -> str:
    """Allocate and return a new unique payment id"""
    return shortuuid.ShortUUID().random(length=7)

def create_payment_record(
        order_id: str,
        status: str,
        amount: str,
        last4: str,
        cardholder_name: str,
) -> Dict[str, Any]:
    """Create and store a new payment record
    Raw card details are never stored: only last4 and cardholder name"""

    payment_id = _alloc_payment_id()

    record: Dict[str, Any] = {
        "payment_id": payment_id,
        "order_id": order_id,
        "status": status,
        "amount": amount,
        "last4": last4,
        "cardholder_name": cardholder_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    payment_data._PAYMENTDB[payment_id] = record
    return record

def get_payment_record(payment_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a payment record by payment id"""
    return payment_data._PAYMENTDB.get(payment_id)

def get_payment_by_order_id(order_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a payment record by order id"""
    for record in payment_data._PAYMENTDB.values():
        if record["order_id"] == order_id:
            return record
    return None

def list_payment_records() -> List[Dict[str, Any]]:
    """Return all payment records"""
    return list(payment_data._PAYMENTDB.values())

def create_card_token(card_number: str) -> str:
    """Generate and store a token representing a card number."""
    card_token = shortuuid.ShortUUID().random(length=12)
    payment_data._TOKENDB[card_token] = card_number
    return card_token

def resolve_card_token(card_token: str) -> Optional[str]:
    """Retrieve the card number associated with a token."""
    return payment_data._TOKENDB.get(card_token)
