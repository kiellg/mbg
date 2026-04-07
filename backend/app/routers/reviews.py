"""Router for handling review-related endpoints."""
from typing import List
from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services import review_service

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("", response_model=ReviewResponse, status_code=201)
def submit_review(
    payload: ReviewCreate,
    current_user: dict=Depends(get_current_user)):
    """Endpoint to submit a new review for an order"""
    return review_service.submit_review(
        customer_id=current_user["user_id"],
        payload=payload,
    )

@router.get("/restaurant/{restaurant_id}", response_model=List[ReviewResponse])
def get_restaurant_reviews(restaurant_id: int):
    """Endpoint to fetch all reviews for a given restaurant"""
    return review_service.get_restaurant_reviews(restaurant_id)
