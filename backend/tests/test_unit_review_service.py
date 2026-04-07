"""This module contains unit tests for the review service layer."""

import pytest
from fastapi import HTTPException
from app.services import review_service
from app.schemas.review import ReviewCreate
from app.schemas.order import OrderStatus

CUSTOMER_ID = "cust123"
OTHER_CUSTOMER_ID = "cust456"

FAKE_ORDER_DELIVERED = {
    "order_id": "order_delivered",
    "customer_id": CUSTOMER_ID,
    "status": OrderStatus.DELIVERED.value,
}

FAKE_ORDER_PENDING = {
    "order_id": "order_pending",
    "customer_id": CUSTOMER_ID,
    "status": OrderStatus.PENDING.value,
}

FAKE_REVIEW_RECORD = {
    "review_id": "review123",
    "customer_id": CUSTOMER_ID,
    "order_id": FAKE_ORDER_DELIVERED["order_id"],
    "restaurant_id": 1,
    "rating": 5,
    "comment": "Great food!",
    "created_at": "2026-04-06T00:00:00+00:00",
}

FAKE_PAYLOAD = ReviewCreate(
    order_id=FAKE_ORDER_DELIVERED["order_id"],
    restaurant_id=1,
    rating=5,
    comment="Great food!"
)

def test_get_average_rating_returns_correct_value(mocker):
    """Test that get_average_rating calculates the average correctly"""
    mocker.patch.object(review_service.review_repo, "get_reviews_by_restaurant", return_value=[
        {"rating": 5},
        {"rating": 4},
        {"rating": 3},
    ])
    avg_rating = review_service.get_average_rating(1)
    assert avg_rating == 4.0

def test_get_average_rating_returns_zero_when_no_reviews(mocker):
    """Test that get_average_rating returns 0.0 when there are no reviews"""
    mocker.patch.object(review_service.review_repo, "get_reviews_by_restaurant", return_value=[])
    avg_rating = review_service.get_average_rating(1)
    assert avg_rating == 0.0

def test_get_average_rating_rounds_to_two_decimal_places(mocker):
    """Test that get_average_rating rounds the result to two decimal places"""
    mocker.patch.object(review_service.review_repo, "get_reviews_by_restaurant", return_value=[
        {"rating": 4},
        {"rating": 4},
        {"rating": 5},
    ])
    avg_rating = review_service.get_average_rating(1)
    assert avg_rating == 4.33

def test_submit_review_success(mocker):
    """Test that submit_review successfully creates a review and updates restaurant rating"""
    mocker.patch.object(review_service.order_repo, "get_order_record",
                        return_value=FAKE_ORDER_DELIVERED)
    mocker.patch.object(review_service.review_repo, "get_review_by_order",
                        return_value=None)
    mocker.patch.object(review_service.review_repo, "create_review_record",
                        return_value=FAKE_REVIEW_RECORD)
    mocker.patch.object(review_service.review_repo, "get_reviews_by_restaurant",
                        return_value=[FAKE_REVIEW_RECORD])
    mock_update = mocker.patch.object(review_service.restaurant_repo,
                                      "update_restaurant_rating")

    response = review_service.submit_review(CUSTOMER_ID, FAKE_PAYLOAD)

    assert response.review_id == "review123"
    assert response.rating == 5
    mock_update.assert_called_once_with(1, 5.0)

def test_submit_review_raises_404_if_order_not_found(mocker):
    """Test that submit_review raises 404 if the order does not exist"""
    mocker.patch.object(review_service.order_repo, "get_order_record", return_value=None)
    with pytest.raises(HTTPException) as exc_info:
        review_service.submit_review(CUSTOMER_ID, FAKE_PAYLOAD)
    assert exc_info.value.status_code == 404

def test_submit_review_raises_403_if_not_authorized(mocker):
    """Test that submit_review raises 403 if the customer is not the owner of the order"""
    mocker.patch.object(review_service.order_repo, "get_order_record",
                        return_value=FAKE_ORDER_DELIVERED)
    with pytest.raises(HTTPException) as exc_info:
        review_service.submit_review(OTHER_CUSTOMER_ID, FAKE_PAYLOAD)
    assert exc_info.value.status_code == 403

def test_submit_review_raises_400_if_order_not_delivered(mocker):
    """Test that submit_review raises 400 if the order is not in Delivered status"""
    mocker.patch.object(review_service.order_repo, "get_order_record",
                        return_value=FAKE_ORDER_PENDING)
    with pytest.raises(HTTPException) as exc_info:
        review_service.submit_review(CUSTOMER_ID, FAKE_PAYLOAD)
    assert exc_info.value.status_code == 400

def test_submit_review_raises_400_if_review_already_exists(mocker):
    """Test that submit_review raises 400 if a review for the order already exists"""
    mocker.patch.object(review_service.order_repo, "get_order_record",
                        return_value=FAKE_ORDER_DELIVERED)
    mocker.patch.object(review_service.review_repo, "get_review_by_order",
                        return_value=FAKE_REVIEW_RECORD)
    with pytest.raises(HTTPException) as exc_info:
        review_service.submit_review(CUSTOMER_ID, FAKE_PAYLOAD)
    assert exc_info.value.status_code == 400

def test_get_restaurant_reviews_returns_sorted_reviews(mocker):
    """Test that get_restaurant_reviews returns reviews sorted by creation date"""
    mocker.patch.object(review_service.review_repo, "get_reviews_by_restaurant",
                        return_value=[
                            {**FAKE_REVIEW_RECORD,
                             "review_id": "r1", "created_at": "2026-04-01T00:00:00+00:00"},
                            {**FAKE_REVIEW_RECORD,
                             "review_id": "r2", "created_at": "2026-04-06T00:00:00+00:00"},
                        ])
    result = review_service.get_restaurant_reviews(1)
    assert result[0].review_id == "r2"
    assert result[1].review_id == "r1"

def test_get_restaurant_reviews_returns_empty_list_when_no_reviews(mocker):
    """Test that get_restaurant_reviews returns an empty list when there are no reviews"""
    mocker.patch.object(review_service.review_repo, "get_reviews_by_restaurant", return_value=[])
    result = review_service.get_restaurant_reviews(1)
    assert not result
