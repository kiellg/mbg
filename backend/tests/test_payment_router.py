# pylint: disable=unused-argument
"""Unit tests for payment_router.py with mocked service and auth."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app.dependencies import get_current_user
from backend.main import app
from backend.app.schemas.payment import PaymentReceipt, PaymentResponse, PaymentStatus

CUSTOMER_ID = "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"

FAKE_PAYMENT_RESPONSE = PaymentResponse(
    payment_id="visa123",
    order_id="abc1234",
    status=PaymentStatus.ACCEPTED,
    amount=Decimal("25.99"),
    last4="1234",
    timestamp=datetime.now(timezone.utc),
)

FAKE_DECLINED_RESPONSE = PaymentResponse(
    payment_id="visa456",
    order_id="abc1234",
    status=PaymentStatus.DECLINED,
    amount=Decimal("25.99"),
    last4="0000",
    timestamp=datetime.now(timezone.utc),
)

FAKE_RECEIPT = PaymentReceipt(
    payment_id="visa123",
    order_id="abc1234",
    amount=Decimal("25.99"),
    last4="1234",
    cardholder_name="John Doe",
    timestamp=datetime.now(timezone.utc),
)

VALID_PAYMENT_PAYLOAD = {
    "card_number": "1234567891011121",
    "expiry_date": "12/99",
    "cvv": "123",
    "cardholder_name": "John Doe",
}

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_auth():
    """Override auth dependency for all tests in this file."""
    app.dependency_overrides[get_current_user] = lambda: {"user_id": CUSTOMER_ID}
    yield
    app.dependency_overrides.clear()


_SVC = "backend.app.routers.payments.payment_service"

# for POST /payments/{order_id}

@patch(f"{_SVC}.process_payment")
def test_process_payment_returns_201_and_accepted(mock_process):
    """Should return 201 with Accepted status for a valid payment."""
    mock_process.return_value = FAKE_PAYMENT_RESPONSE

    response = client.post("/payments/abc1234", json=VALID_PAYMENT_PAYLOAD)

    assert response.status_code == 201
    assert response.json()["status"] == "Accepted"
    assert response.json()["last4"] == "1234"


@patch(f"{_SVC}.process_payment")
def test_process_payment_returns_201_and_declined(mock_process):
    """Should return 201 with Declined status for a card ending in 0000."""
    mock_process.return_value = FAKE_DECLINED_RESPONSE

    response = client.post("/payments/abc1234", json=VALID_PAYMENT_PAYLOAD)

    assert response.status_code == 201
    assert response.json()["status"] == "Declined"


@patch(f"{_SVC}.process_payment")
def test_process_payment_passes_correct_args_to_service(mock_process):
    """Should pass order_id, customer_id, and payload to the service."""
    mock_process.return_value = FAKE_PAYMENT_RESPONSE

    client.post("/payments/abc1234", json=VALID_PAYMENT_PAYLOAD)

    mock_process.assert_called_once()
    call_kwargs = mock_process.call_args.kwargs
    assert call_kwargs["order_id"] == "abc1234"
    assert call_kwargs["customer_id"] == CUSTOMER_ID


@patch(f"{_SVC}.process_payment")
def test_process_payment_raises_404_if_order_not_found(mock_process):
    """Should propagate 404 from the service when order does not exist."""
    mock_process.side_effect = HTTPException(status_code=404, detail="Order not found")

    response = client.post("/payments/whoisthis", json=VALID_PAYMENT_PAYLOAD)

    assert response.status_code == 404


@patch(f"{_SVC}.process_payment")
def test_process_payment_raises_403_if_wrong_customer(mock_process):
    """Should propagate 403 from the service when order belongs to a different customer."""
    mock_process.side_effect = HTTPException(
        status_code=403, detail="Not authorized to pay for this order."
    )

    response = client.post("/payments/abc1234", json=VALID_PAYMENT_PAYLOAD)

    assert response.status_code == 403


@patch(f"{_SVC}.process_payment")
def test_process_payment_raises_400_if_order_not_pending(mock_process):
    """Should propagate 400 from the service when order is not Pending."""
    mock_process.side_effect = HTTPException(
        status_code=400, detail="Payment can only be made for Pending orders."
    )

    response = client.post("/payments/abc1234", json=VALID_PAYMENT_PAYLOAD)

    assert response.status_code == 400


@patch(f"{_SVC}.process_payment")
def test_process_payment_raises_400_for_invalid_card(mock_process):
    """Should propagate 400 from the service for invalid card details."""
    mock_process.side_effect = HTTPException(
        status_code=400, detail="Invalid card number. Must be exactly 16 digits."
    )

    response = client.post("/payments/abc1234", json=VALID_PAYMENT_PAYLOAD)

    assert response.status_code == 400

# for GET /payments/{order_id}/receipt

@patch(f"{_SVC}.get_receipt")
def test_get_receipt_returns_200_and_receipt(mock_get_receipt):
    """Should return 200 with the receipt for a successfully paid order."""
    mock_get_receipt.return_value = FAKE_RECEIPT

    response = client.get("/payments/abc1234/receipt")

    assert response.status_code == 200
    assert response.json()["payment_id"] == "visa123"
    assert response.json()["last4"] == "1234"
    assert response.json()["message"] == "Payment accepted. Your order is being prepared."


@patch(f"{_SVC}.get_receipt")
def test_get_receipt_passes_correct_args_to_service(mock_get_receipt):
    """Should pass order_id and customer_id to the service."""
    mock_get_receipt.return_value = FAKE_RECEIPT

    client.get("/payments/abc1234/receipt")

    mock_get_receipt.assert_called_once_with(
        order_id="abc1234",
        customer_id=CUSTOMER_ID,
    )


@patch(f"{_SVC}.get_receipt")
def test_get_receipt_raises_404_if_no_accepted_payment(mock_get_receipt):
    """Should propagate 404 when no accepted payment exists for the order."""
    mock_get_receipt.side_effect = HTTPException(
        status_code=404, detail="No accepted payment found for this order."
    )

    response = client.get("/payments/abc1234/receipt")

    assert response.status_code == 404


@patch(f"{_SVC}.get_receipt")
def test_get_receipt_raises_403_if_wrong_customer(mock_get_receipt):
    """Should propagate 403 when receipt belongs to a different customer."""
    mock_get_receipt.side_effect = HTTPException(
        status_code=403, detail="Not authorized to view this receipt."
    )

    response = client.get("/payments/abc1234/receipt")

    assert response.status_code == 403
