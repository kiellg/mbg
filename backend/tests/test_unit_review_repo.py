"""Unit tests for the review repository functions."""
#pylint: disable=unused-variable
import pytest
from app.data import review_data
from app.repositories import review_repo

@pytest.fixture(autouse=True)
def reset_db():
    """Reset the in-memory review database before each test"""
    review_data.REVIEW_DB.clear()
    yield

def test_create_review_record_stores_and_returns_review():
    """Test that creating a review record stores it in the DB and returns the record"""
    review = review_repo.create_review_record(
        customer_id="cust123",
        order_id="order456",
        restaurant_id=1,
        rating=5,
        comment="Delicious!"
    )
    assert "review_id" in review
    assert review["customer_id"] == "cust123"
    assert review["order_id"] == "order456"
    assert review["restaurant_id"] == 1
    assert review["rating"] == 5
    assert review["comment"] == "Delicious!"
    assert "created_at" in review

def test_create_review_record_stores_in_db():
    """Test that the created review record is stored in the in-memory DB"""
    review = review_repo.create_review_record(
        customer_id="cust123",
        order_id="order456",
        restaurant_id=1,
        rating=5,
        comment=None,
    )
    assert review["review_id"] in review_data.REVIEW_DB

def test_create_review_record_with_no_comment():
    """Test that creating a review record with no comment works correctly"""
    review = review_repo.create_review_record(
        customer_id="cust123",
        order_id="order456",
        restaurant_id=1,
        rating=4,
        comment=None,
    )
    assert review["comment"] is None

def test_create_review_record_ids_are_unique():
    """Test that multiple created review records have unique IDs"""
    review1 = review_repo.create_review_record(
        customer_id="cust123",
        order_id="order456",
        restaurant_id=1,
        rating=5,
        comment="Great!"
    )
    review2 = review_repo.create_review_record(
        customer_id="cust789",
        order_id="order012",
        restaurant_id=2,
        rating=4,
        comment="Good!"
    )
    assert review1["review_id"] != review2["review_id"]

def test_get_review_by_id_returns_correct_review():
    """Test that fetching a review by ID returns the correct review"""
    review = review_repo.create_review_record(
        customer_id="cust123",
        order_id="order456",
        restaurant_id=1,
        rating=5,
        comment="Excellent!"
    )
    fetched_review = review_repo.get_review_by_id(review["review_id"])
    assert fetched_review == review

def test_get_review_by_id_returns_none_for_nonexistent_id():
    """Test that fetching a review by a nonexistent ID returns None"""
    assert review_repo.get_review_by_id("nonexistent_id") is None

def test_get_review_by_order_returns_correct_review():
    """Test that fetching a review by order ID returns the correct review"""
    review = review_repo.create_review_record(
        customer_id="cust123",
        order_id="order456",
        restaurant_id=1,
        rating=5,
        comment="Fantastic!"
    )
    fetched_review = review_repo.get_review_by_order("order456")
    assert fetched_review == review

def test_get_review_by_order_returns_none_for_nonexistent_order():
    """Test that fetching a review by a nonexistent order ID returns None"""
    assert review_repo.get_review_by_order("nonexistent_order") is None

def test_get_reviews_by_restaurant_returns_all_reviews_for_restaurant():
    """Test that fetching reviews by restaurant ID returns all reviews for that restaurant"""
    review1 = review_repo.create_review_record(
        customer_id="cust123",
        order_id="order456",
        restaurant_id=1,
        rating=5,
        comment="Amazing!"
    )
    review2 = review_repo.create_review_record(
        customer_id="cust789",
        order_id="order012",
        restaurant_id=1,
        rating=4,
        comment="Very good!"
    )
    review3 = review_repo.create_review_record(
        customer_id="cust456",
        order_id="order789",
        restaurant_id=2,
        rating=3,
        comment="Average."
    )
    reviews_for_restaurant_1 = review_repo.get_reviews_by_restaurant(1)
    assert len(reviews_for_restaurant_1) == 2
    assert review1 in reviews_for_restaurant_1
    assert review2 in reviews_for_restaurant_1

def test_get_reviews_by_restaurant_returns_empty_list_for_no_reviews():
    """Test that fetching reviews for a restaurant with no reviews returns an empty list"""
    assert review_repo.get_reviews_by_restaurant("nonexistent_restaurant") == []
