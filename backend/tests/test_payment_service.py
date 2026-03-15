#pylint: disable=unused-argument
"""Unit test for payment_service.py"""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from backend.app.schemas.payment import PaymentRequest, PaymentStatus
from backend.app.services import payment_service

CUSTOMER_ID = "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"

FAKE_ORDER = {
    "order_id": "abc1234",
    "customer_id": CUSTOMER_ID,
    "status": "Pending",
    "total": "25.99",
}

FAKE_PAYMENT_RECORD = {
    "payment_id": "visa123",
    "order_id": "abc1234",
    "status": "Accepted",
    "amount": "25.99",
    "last4": "1234",
    "cardholder_name": "John Doe",
    "timestamp": datetime.now(timezone.utc).isoformat(),
}

VALID_PAYLOAD = PaymentRequest(
    card_number="1234567891011121",
    expiry_date="12/99",
    cvv="123",
    cardholder_name="John Doe",
)

INVALID_PAYLOAD = PaymentRequest(
    card_number="1234567891010000",
    expiry_date="12/99",
    cvv="123",
    cardholder_name="John Doe",
)

# for _validate_card_number
def test_validate_card_number_accepts_16_digits():
    """Should not raise for a valid 16 digit card number."""
    payment_service._validate_card_number("1234567891011121")

def test_validate_card_number_rejects_less_than_16_digits():
    """Should raise 400 for card number less than 16 digits."""
    with pytest.raises(HTTPException) as exc:
        payment_service._validate_card_number("12345678")
    assert exc.value.status_code == 400

def test_validate_card_number_rejects_more_than_16_digits():
    """Should raise 400 for card number more than 16 digits."""
    with pytest.raises(HTTPException) as exc:
        payment_service._validate_card_number("12345678910111213")
    assert exc.value.status_code == 400

def test_validate_card_number_rejects_non_digits():
    """Should raise 400 for card number with non digit characters"""
    with pytest.raises(HTTPException) as exc:
        payment_service._validate_card_number("123456789101112p")
    assert exc.value.status_code == 400

# for _validate_expiry_date
def test_validate_expiry_date_accepts_valid_future_date():
    """Should not raise for a valid future expiry date."""
    payment_service._validate_expiry_date("12/99")

def test_validate_expiry_date_rejects_wrong_format():
    """Should raise 400 for expiry date for wrong format."""
    with pytest.raises(HTTPException) as exc:
        payment_service._validate_expiry_date("1299")
    assert exc.value.status_code == 400

def test_validate_expiry_date_rejects_invalid_month():
    """Should raise 400 for expiry date for invalid month."""
    with pytest.raises(HTTPException) as exc:
        payment_service._validate_expiry_date("13/99")
    assert exc.value.status_code == 400

def test_validate_expiry_date_rejects_expired_card():
    """Should raise 400 for expiry date for expired card."""
    with pytest.raises(HTTPException) as exc:
        payment_service._validate_expiry_date("12/02")
    assert exc.value.status_code == 400

# for _validate_cvv
def test_validate_cvv_accepts_3_digits():
    """SHould not raise for a valid 3 digit cvv."""
    payment_service._validate_cvv("123")

def test_validate_cvv_accepts_4_digits():
    """SHould not raise for a valid 4 digit cvv."""
    payment_service._validate_cvv("1234")

def test_validate_cvv_rejects_2_digits():
    """Should raise 400 for a cvv shorter than 2 digits."""
    with pytest.raises(HTTPException) as exc:
        payment_service._validate_cvv("12")
    assert exc.value.status_code == 400

def test_validate_cvv_rejects_non_digits():
    """SHould raise 400 for a cvv containing non digit characters."""
    with pytest.raises(HTTPException) as exc:
        payment_service._validate_cvv("12a")
    assert exc.value.status_code == 400

# for _simulate_payment
def test_simulate_payments_accepts_normal_card():
    """Should return Accepted for a card not ending in 0000."""
    result = payment_service._simulate_payment("1234567891011121")
    assert result == PaymentStatus.ACCEPTED

def test_simulate_payments_declines_card_ending_in_0000():
    """Should return Declined for a card ending in 0000"""
    result = payment_service._simulate_payment("1234567891010000")

# for process_payment
@patch("backend.app.services.payment_service.payment_repo")
@patch("backend.app.services.payment_service.order_repo")
def test_process_payment_accepted(mock_order_repo, mock_payment_repo):
    """Should create a payment record and return Accepted status."""
    mock_order_repo.get_order_record.return_value = FAKE_ORDER
    mock_payment_repo.create_payment_record.return_value = FAKE_PAYMENT_RECORD

    result = payment_service.process_payment(
        order_id="abc1234",
        customer_id=CUSTOMER_ID,
        payload=VALID_PAYLOAD,
    )

    assert result.status == PaymentStatus.ACCEPTED
    assert result.last4 == "1234"
    mock_payment_repo.create_payment_record.assert_called_once()

@patch("backend.app.services.payment_service.payment_repo")
@patch("backend.app.services.payment_service.order_repo")
def test_process_payment_declined(mock_order_repo, mock_payment_repo):
    """Should create a payment record and return Declined status."""
    mock_order_repo.get_order_record.return_value = FAKE_ORDER
    mock_payment_repo.create_payment_record.return_value = {
        **FAKE_PAYMENT_RECORD,
        "status": "Declined",
        "last4": "0000"
    }

    result = payment_service.process_payment(
        order_id="abc1234",
        customer_id=CUSTOMER_ID,
        payload=INVALID_PAYLOAD,
    )

    assert result.status == PaymentStatus.DECLINED

@patch("backend.app.services.payment_service.order_repo")
def test_process_payment_raises_404_if_order_not_found(mock_order_repo):
    """Should raise 404 when the order does not exist."""
    mock_order_repo.get_order_record.return_value = None

    with pytest.raises(HTTPException) as exc:
        payment_service.process_payment(
            order_id="randomorder",
            customer_id=CUSTOMER_ID,
            payload=VALID_PAYLOAD,
        )
    assert exc.value.status_code == 404

@patch("backend.app.services.payment_service.order_repo")
def test_process_payment_raises_404_if_customer_is_wrong(mock_order_repo):
    """Should raise 404 when the customer is wrong."""
    mock_order_repo.get_order_record.return_value = FAKE_ORDER

    with pytest.raises(HTTPException) as exc:
        payment_service.process_payment(
            order_id="abc1234",
            customer_id="whoisthis",
            payload=VALID_PAYLOAD,
        )
    assert exc.value.status_code == 403