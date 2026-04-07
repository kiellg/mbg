"""Integration tests for the review flow — router → service → repo → data."""
# pylint: disable=protected-access

from fastapi.testclient import TestClient

from main import app
from app.dependencies import get_current_user
from app.data import review_data, order_data, restaurants_data
from app.repositories import restaurant_repo, review_repo
from app.schemas.order import OrderStatus

client = TestClient(app)

CUSTOMER_ID = "user-001"
OTHER_CUSTOMER_ID = "user-999"


def setup_function():
    """Reset all in-memory state and override auth before each test."""
    review_data.REVIEW_DB.clear()
    restaurant_repo.reset_restaurants()
    app.dependency_overrides[get_current_user] = lambda: {"user_id": CUSTOMER_ID}

    order_data._ORDERDB["order-abc"] = {
        "order_id": "order-abc",
        "customer_id": CUSTOMER_ID,
        "restaurant_id": 1,
        "status": OrderStatus.DELIVERED.value,
    }


def teardown_function():
    app.dependency_overrides.clear()


def test_submit_review_creates_review_and_updates_restaurant_rating():
    response = client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 4,
        "comment": "Solid meal.",
    })
    assert response.status_code == 201
    assert response.json()["rating"] == 4
    assert response.json()["restaurant_id"] == 1

    restaurant = restaurant_repo.get_restaurant_record(1)
    assert restaurant["rating"] == 4.0


def test_submit_review_persists_in_review_db():
    client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 5,
        "comment": "Amazing!",
    })
    reviews = review_repo.get_reviews_by_restaurant(1)
    assert len(reviews) == 1
    assert reviews[0]["rating"] == 5
    assert reviews[0]["customer_id"] == CUSTOMER_ID


def test_submit_review_returns_404_when_order_not_found():
    response = client.post("/reviews", json={
        "order_id": "order-does-not-exist",
        "rating": 5,
        "comment": "??",
    })
    assert response.status_code == 404


def test_submit_review_returns_403_when_wrong_customer():
    app.dependency_overrides[get_current_user] = lambda: {"user_id": OTHER_CUSTOMER_ID}
    response = client.post("/reviews", json={
        "order_id": "order-abc",
        "rating": 5,
        "comment": "Not my order.",
    })
    assert response.status_code == 403


def test_submit_review_returns_400_when_order_not_delivered():
    order_data._ORDERDB["order-pending"] = {
        "order_id": "order-pending",
        "customer_id": CUSTOMER_ID,
        "restaurant_id": 1,
        "status": OrderStatus.PENDING.value,
    }
    response = client.post("/reviews", json={
        "order_id": "order-pending",
        "rating": 3,
        "comment": "Too soon.",
    })
    assert response.status_code == 400


def test_submit_review_returns_400_when_duplicate_review():
    client.post("/reviews", json={"order_id": "order-abc", "rating": 5, "comment": "First!"})
    response = client.post("/reviews", json={"order_id": "order-abc", "rating": 3, "comment": "Again!"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_restaurant_rating_updates_with_average_across_multiple_reviews():
    order_data._ORDERDB["order-xyz"] = {
        "order_id": "order-xyz",
        "customer_id": CUSTOMER_ID,
        "restaurant_id": 1,
        "status": OrderStatus.DELIVERED.value,
    }
    client.post("/reviews", json={"order_id": "order-abc", "rating": 4, "comment": "Good."})
    client.post("/reviews", json={"order_id": "order-xyz", "rating": 2, "comment": "Meh."})

    restaurant = restaurant_repo.get_restaurant_record(1)
    assert restaurant["rating"] == 3.0  # (4 + 2) / 2


def test_get_restaurant_reviews_returns_sorted_newest_first():
    order_data._ORDERDB["order-xyz"] = {
        "order_id": "order-xyz",
        "customer_id": CUSTOMER_ID,
        "restaurant_id": 1,
        "status": OrderStatus.DELIVERED.value,
    }
    client.post("/reviews", json={"order_id": "order-abc", "rating": 3, "comment": "First review."})
    client.post("/reviews", json={"order_id": "order-xyz", "rating": 5, "comment": "Second review."})

    response = client.get("/reviews/restaurant/1")
    assert response.status_code == 200
    reviews = response.json()
    assert len(reviews) == 2
    assert reviews[0]["comment"] == "Second review." 


def test_get_restaurant_reviews_returns_empty_for_no_reviews():
    response = client.get("/reviews/restaurant/1")
    assert response.status_code == 200
    assert response.json() == []


def test_get_restaurant_reviews_is_public():
    """Public endpoint — accessible without auth."""
    app.dependency_overrides.clear()
    response = client.get("/reviews/restaurant/1")
    assert response.status_code == 200
