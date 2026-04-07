"""This module implements the business logic for handling reviews."""

from typing import List
from fastapi import HTTPException
from app.repositories import review_repo, order_repo, restaurant_repo
from app.schemas.review import ReviewCreate, ReviewResponse
from app.schemas.order import OrderStatus

def _build_review_response(review_record: dict) -> ReviewResponse:
    """Helper function to convert a review record dict to a ReviewResponse schema"""
    return ReviewResponse(
        review_id=review_record["review_id"],
        customer_id=review_record["customer_id"],
        order_id=review_record["order_id"],
        restaurant_id=review_record["restaurant_id"],
        rating=review_record["rating"],
        comment=review_record["comment"],
        created_at=review_record["created_at"],
    )

def get_average_rating(restaurant_id: int) -> float:
    """Calculate and return the average rating for a restaurant"""
    reviews = review_repo.get_reviews_by_restaurant(restaurant_id)
    if not reviews:
        return 0.0
    return round(sum(review["rating"] for review in reviews) / len(reviews), 2)

def submit_review(customer_id: str, payload: ReviewCreate) -> ReviewResponse:
    """Submit a new review for an order"""
    order = order_repo.get_order_record(payload.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order["customer_id"] != customer_id:
        raise HTTPException(status_code=403, detail="Not authorized to review this order")

    if order["status"] != OrderStatus.DELIVERED.value:
        raise HTTPException(status_code=400,
                            detail="Order must be Delivered before leaving a review")

    if review_repo.get_review_by_order(payload.order_id):
        raise HTTPException(status_code=400, detail="A review for this order already exists")

    review_record = review_repo.create_review_record(
        customer_id=customer_id,
        order_id=payload.order_id,
        restaurant_id=payload.restaurant_id,
        rating=payload.rating,
        comment=payload.comment,
    )

    new_rating = get_average_rating(payload.restaurant_id)
    restaurant_repo.update_restaurant_rating(payload.restaurant_id, new_rating)
    return _build_review_response(review_record)

def get_restaurant_reviews(restaurant_id: int) -> List[ReviewResponse]:
    """Fetch all reviews for a given restaurant"""
    review_records = review_repo.get_reviews_by_restaurant(restaurant_id)
    sorted_reviews = sorted(review_records, key=lambda r: r["created_at"], reverse=True)
    return [_build_review_response(record) for record in sorted_reviews]
