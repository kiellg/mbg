"""Unit tests for the review router endpoints."""

from datetime import datetime, timezone

import pytest
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
    app.dependency_overrides[get_current_user] = lambda: {"user_id": CUSTOMER_ID}


def teardown_function():
    app.dependency_overrides.clear()


def test_submit_review_returns_201(mocker):
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
    mocker.patch.object(reviews.review_service, "submit_review",
                        side_effect=HTTPException(status_code=404, detail="Order not found"))
    response = client.post("/reviews", json={
        "order_id": "order-missing",
        "rating": 5,
        "comment": "Great food!",
    })
    assert response.status_code == 404


def test_submit_review_returns_403_when_not_authorized(mocker):
    mocker.patch.object(reviews.review_service, "submit_review",
                        side_effect=HTTPException(status_code=403, detail="Not authorized"))
    response = client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 5,
        "comment": "Great food!",
    })
    assert response.status_code == 403


def test_submit_review_returns_400_when_already_reviewed(mocker):
    mocker.patch.object(reviews.review_service, "submit_review",
                        side_effect=HTTPException(status_code=400, detail="A review for this order already exists"))
    response = client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 5,
        "comment": "Great food!",
    })
    assert response.status_code == 400


def test_submit_review_returns_422_when_rating_out_of_range():
    response = client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 10,  # exceeds le=5
        "comment": "Too good!",
    })
    assert response.status_code == 422


def test_submit_review_requires_auth():
    app.dependency_overrides.clear()
    response = client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 5,
        "comment": "Great food!",
    })
    assert response.status_code == 401


def test_get_restaurant_reviews_returns_200(mocker):
    mocker.patch.object(reviews.review_service, "get_restaurant_reviews",
                        return_value=[FAKE_REVIEW_RESPONSE])
    response = client.get("/reviews/restaurant/1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["review_id"] == "review-uuid-001"


def test_get_restaurant_reviews_returns_empty_list(mocker):
    mocker.patch.object(reviews.review_service, "get_restaurant_reviews",
                        return_value=[])
    response = client.get("/reviews/restaurant/99")
    assert response.status_code == 200
    assert response.json() == []


def test_get_restaurant_reviews_returns_422_for_invalid_id():
    response = client.get("/reviews/restaurant/abc")
    assert response.status_code == 422


def test_get_restaurant_reviews_is_public(mocker):
    """Public endpoint — no auth required."""
    app.dependency_overrides.clear()
    mocker.patch.object(reviews.review_service, "get_restaurant_reviews",
                        return_value=[])
    response = client.get("/reviews/restaurant/1")
    assert response.status_code == 200