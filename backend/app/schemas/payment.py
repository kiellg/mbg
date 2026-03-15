"""Schemas for payment request, response, and receipt"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

class PaymentStatus(str, Enum):
    """Valid statuses for payment"""

    ACCEPTED = "Accepted"
    DECLINED = "Declined"

class PaymentRequest(BaseModel):
    """Payment input submitted by the customer"""

    card_number: str = Field(..., description="16-digit card number")
    expiry_date: str = Field(..., description="Expiry date in MM/YY format")
    cvv: str = Field(..., description="3 or 4 digit CVV")
    cardholder_name: str = Field(..., description="Name on the card")

class PaymentResponse(BaseModel):
    """Result returned after processing a payment attempt"""

    payment_id: str
    order_id: str
    status: str
    amount: Decimal
    last4: str
    timestamp: datetime
