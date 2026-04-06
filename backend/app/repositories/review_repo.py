"""This module implements the repository functions for managing review data."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

from app.data import review_data

def get_review_by_id(review_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a review by its ID"""
    return review_data.REVIEW_DB.get(review_id)

def get_review_by_order(order_id:str) -> Optional[Dict[str, Any]]:
    """Retrieve a review by its associated order ID"""
    for review in review_data.REVIEW_DB.values():
        if review["order_id"] == order_id:
            return review
    return None

def get_reviews_by_restaurant(restaurant_id: int) -> List[Dict[str, Any]]:
    """Retrieve all reviews for a given restaurant"""
    return [
        review for review in review_data.REVIEW_DB.values()
        if review["restaurant_id"] == restaurant_id
    ]

def create_review_record(
    customer_id: str,
    order_id: str,
    restaurant_id: int,
    rating: int,
    comment: Optional[str],
) -> Dict[str, Any]:
    """Create and store a new review record"""
    review_id = str(uuid.uuid4())
    review_record = {
        "review_id": review_id,
        "customer_id": customer_id,
        "order_id": order_id,
        "restaurant_id": restaurant_id,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    review_data.REVIEW_DB[review_id] = review_record
    return review_record
