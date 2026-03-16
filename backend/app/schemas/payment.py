#pylint: disable=unused-import
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
    status: PaymentStatus
    amount: Decimal
    last4: str
    timestamp: datetime

class PaymentReceipt(BaseModel):
    """Mock receipt generated on successful payment."""

    payment_id: str
    order_id: str
    amount: Decimal
    last4: str
    cardholder_name: str
    timestamp: datetime
    message: str = "Payment accepted. Your order is being prepared."

class SavedPaymentMethod(BaseModel):
    """A saved dummy payment method for reuse."""

    saved_method_id: str
    last4: str
    expiry_date: str
    cardholder_name: str
    nickname: Optional[str] = None

class SavedPaymentMethodRequest(BaseModel):
    """Request payload for saving a payment method."""

    card_number: str = Field(..., description="16 digit card number")
    expiry_date: str = Field(..., description="Expiry date in MM/YY format")
    cvv: str = Field(..., description="3 or 4 digit CVV")
    cardholder_name: str = Field(..., description="Name on the card")
    nickname: Optional[str] = Field(None, description="Optional nickname e.g. RBC Visa")
