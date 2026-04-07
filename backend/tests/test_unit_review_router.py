"""Unit tests for the review router endpoints."""

from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app
from app.dependencies import get_current_user
from app.schemas.review import ReviewResponse
from app.routers import reviews

client = TestClient(app)

CUSTOMER_ID = "user-001"

FAKE_REVIEW_RESPONSE = ReviewResponse(
    review_id="review-uuid-001",
    customer_id=CUSTOMER_ID,
    order_id="order-abc",
    restaurant_id=1,
    rating=5,
    comment="Great food!",
    created_at=datetime.now(timezone.utc),
)


def setup_function():
    """Override auth dependency before each test."""
    app.dependency_overrides[get_current_user] = lambda: {"user_id": CUSTOMER_ID}


def teardown_function():
    """Clear any overrides after each test."""
    app.dependency_overrides.clear()


def test_submit_review_returns_201(mocker):
    """Test that submitting a review returns a 201 status code and the expected response."""
    mocker.patch.object(reviews.review_service, "submit_review",
                        return_value=FAKE_REVIEW_RESPONSE)
    response = client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 5,
        "comment": "Great food!",
    })
    assert response.status_code == 201
    assert response.json()["review_id"] == "review-uuid-001"


def test_submit_review_calls_service_with_correct_args(mocker):
    """Test that the submit_review endpoint calls the review service
    with the correct arguments."""
    mock_submit = mocker.patch.object(reviews.review_service, "submit_review",
                                      return_value=FAKE_REVIEW_RESPONSE)
    client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 5,
        "comment": "Great food!",
    })
    mock_submit.assert_called_once()
    call_kwargs = mock_submit.call_args
    assert call_kwargs.kwargs["customer_id"] == CUSTOMER_ID


def test_submit_review_returns_404_when_order_not_found(mocker):
    """Test that submitting a review for a non-existent order returns a 404 status code."""
    mocker.patch.object(reviews.review_service, "submit_review",
                        side_effect=HTTPException(status_code=404, detail="Order not found"))
    response = client.post("/reviews", json={
        "order_id": "order-missing",
        "rating": 5,
        "comment": "Great food!",
    })
    assert response.status_code == 404


def test_submit_review_returns_403_when_not_authorized(mocker):
    """Test that submitting a review for an order that
    the user does not own returns a 403 status code."""
    mocker.patch.object(reviews.review_service, "submit_review",
                        side_effect=HTTPException(status_code=403, detail="Not authorized"))
    response = client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 5,
        "comment": "Great food!",
    })
    assert response.status_code == 403


def test_submit_review_returns_400_when_already_reviewed(mocker):
    """Test that submitting a review for an order that
    already has a review returns a 400 status code."""
    mocker.patch.object(reviews.review_service, "submit_review",
                        side_effect=HTTPException(status_code=400,
                        detail="A review for this order already exists"))
    response = client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 5,
        "comment": "Great food!",
    })
    assert response.status_code == 400


def test_submit_review_returns_422_when_rating_out_of_range():
    """Test that submitting a review with a rating outside the valid range
    returns a 422 status code."""
    response = client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 10,  # exceeds le=5
        "comment": "Too good!",
    })
    assert response.status_code == 422


def test_submit_review_requires_auth():
    """Test that submitting a review without authentication returns a 401 status code."""
    app.dependency_overrides.clear()
    response = client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 5,
        "comment": "Great food!",
    })
    assert response.status_code == 401


def test_get_restaurant_reviews_returns_200(mocker):
    """Test that fetching reviews for a restaurant returns a 200 status code
    and the expected response."""
    mock_get =mocker.patch.object(reviews.review_service, "get_restaurant_reviews",
                        return_value=[FAKE_REVIEW_RESPONSE])
    response = client.get("/reviews/restaurant/1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["review_id"] == "review-uuid-001"
    mock_get.assert_called_once_with(1)


def test_get_restaurant_reviews_returns_empty_list(mocker):
    """Test that fetching reviews for a restaurant with no reviews
    returns an empty list."""
    mocker.patch.object(reviews.review_service, "get_restaurant_reviews",
                        return_value=[])
    response = client.get("/reviews/restaurant/99")
    assert response.status_code == 200
    assert response.json() == []


def test_get_restaurant_reviews_returns_422_for_invalid_id():
    """Test that fetching reviews with an invalid restaurant ID
    returns a 422 status code."""
    response = client.get("/reviews/restaurant/abc")
    assert response.status_code == 422


def test_get_restaurant_reviews_is_public(mocker):
    """Public endpoint — no auth required."""
    app.dependency_overrides.clear()
    mocker.patch.object(reviews.review_service, "get_restaurant_reviews",
                        return_value=[])
    response = client.get("/reviews/restaurant/1")
    assert response.status_code == 200

def test_submit_review_returns_422_when_missing_required_fields():
    """Test that submitting a review with missing required fields
    returns a 422 status code."""
    response = client.post("/reviews", json={
        "comment": "No order or rating provided.",
    })
    assert response.status_code == 422

def test_submit_review_returns_422_when_missing_order_id():
    """Test that submitting a review without an order_id
    returns a 422 status code."""
    response = client.post("/reviews", json={
        "rating": 5,
        "comment": "No order id.",
    })
    assert response.status_code == 422

def test_submit_review_returns_422_when_missing_rating():
    """Test that submitting a review without a rating
    returns a 422 status code."""
    response = client.post("/reviews", json={
        "order_id": "order-abc",
        "comment": "No rating provided.",
    })
    assert response.status_code == 422
