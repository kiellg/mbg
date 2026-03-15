#pylint: disable=unused-argument, protected-access
"""Unit test for backend.app.repositories.payment_repo"""

from backend.app.data import payment_data
from backend.app.repositories.payment_repo import (
    create_payment_record,
    get_payment_record,
    get_payment_by_order_id,
    list_payment_records,
)

def setup_function():
    """Clear the payment DB before each test"""
    payment_data._PAYMENTDB.clear()

# for create_payment_record
def test_create_payment_record_stores_record():
    """Should create and store a payment record in the DB."""
    record = create_payment_record(
        order_id="abc1234",
        status="Accepted",
        amount="25.99",
        last4="1234",
        cardholder_name="John Doe",
    )

    assert record["order_id"] == "abc1234"
    assert record["status"] == "Accepted"
    assert record["amount"] == "25.99"
    assert record["last4"] == "1234"
    assert record["cardholder_name"] == "John Doe"
    assert "payment_id" in record
    assert "timestamp" in record

def test_create_payment_record_does_not_store_raw_card_details():
    """Should not store raw card details"""
    record = create_payment_record(
        order_id="abc1234",
        status="Accepted",
        amount="25.99",
        last4="1234",
        cardholder_name="John Doe",
    )

    assert "card_number" not in record
    assert "expiry_date" not in record
    assert "cvv" not in record

def test_create_payment_record_generates_unique_ids():
    """Should generate a unique payment_id for each record."""
    record_1 = create_payment_record(
        order_id="abc1234", status="Accepted",
        amount="25.99", last4="1234", cardholder_name="John Doe",
    )
    record_2 = create_payment_record(
        order_id="xyz5678", status="Declined",
        amount="42.69", last4="5678", cardholder_name="Jane Doe",
    )
    assert record_1["payment_id"] != record_2["payment_id"]

# for get_payment_record
def test_get_payment_record_returns_existing():
    """Should return the correct record by payment_id."""
    record = create_payment_record(
        order_id="abc1234", status="Accepted",
        amount="25.99", last4="1234", cardholder_name="John Doe",
    )

    fetched = get_payment_record(record["payment_id"])
    assert fetched is not None
    assert fetched["payment_id"] == record["payment_id"]

def test_get_payment_record_returns_none_for_missing():
    """Should return None when payment_id does not exist."""
    assert get_payment_record("randomstuff") is None

# for get_payment_by_order_id
def test_get_payment_by_order_id_returns_correct():
    """Should return the correct record associated with the given order_id"""
    record = create_payment_record(
        order_id="abc1234", status="Accepted",
        amount="25.99", last4="1234", cardholder_name="John Doe",
    )

    fetched = get_payment_by_order_id("abc1234")
    assert fetched is not None
    assert fetched["order_id"] == record["order_id"]

def test_get_payment_by_order_id_returns_none_for_missing():
    """Should return None when no payment exists for the given order_id."""
    assert get_payment_by_order_id("randomstuff") is None

# for list_payment_records
def test_list_payment_records_returns_all():
    """Should return all stored payment records."""
    create_payment_record(
        order_id="abc1234", status="Accepted",
        amount="25.99", last4="1234", cardholder_name="John Doe",
    )
    create_payment_record(
        order_id="xyz5678", status="Declined",
        amount="42.69", last4="5678", cardholder_name="Jane Doe",
    )

    records = list_payment_records()
    assert len(records) == 2

def test_list_payment_records_returns_empty_when_no_records():
    """Should return an empty list when no payments exist."""
    assert not list_payment_records()
