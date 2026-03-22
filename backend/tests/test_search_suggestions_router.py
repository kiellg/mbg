"""Tests for search suggestions router"""

from fastapi.testclient import TestClient
from backend.main import app

def test_search_suggestions_success(monkeypatch):
    """Endpoint should return mocked suggestions"""

    def mock_get_search_suggestions(query: str):
        return {
            "suggestions": [
                {
                    "suggestion_type": "restaurant",
                    "id": 1,
                    "name": "Mock Restaurant",
                    "restaurant_id": None,
                },
                {
                    "suggestion_type": "menu_item",
                    "id": 10,
                    "name": "Mock Burger",
                    "restaurant_id": 1,
                },
            ]
        }

    monkeypatch.setattr(
        "backend.app.routers.restaurants.get_search_suggestions",
        mock_get_search_suggestions,
    )

    client = TestClient(app)

    response = client.get("/restaurants/search/suggestions?q=test")

    assert response.status_code == 200

    data = response.json()

    assert "suggestions" in data
    assert len(data["suggestions"]) == 2

    assert data["suggestions"][0]["suggestion_type"] == "restaurant"
    assert data["suggestions"][1]["suggestion_type"] == "menu_item"

def test_search_suggestions_empty_result(monkeypatch):
    """Endpoint should return empty list when no suggestions"""

    def mock_get_search_suggestions(query: str):
        return {"suggestions": []}

    monkeypatch.setattr(
        "backend.app.routers.restaurants.get_search_suggestions",
        mock_get_search_suggestions,
    )

    client = TestClient(app)

    response = client.get("/restaurants/search/suggestions?q=none")

    assert response.status_code == 200
    assert response.json()["suggestions"] == []

def test_search_suggestions_query_param_required():
    """missing query param should return validation error"""
    client = TestClient(app)

    response = client.get("/restaurants/search/suggestions")

    assert response.status_code == 422

def test_search_suggestions_passes_query(monkeypatch):
    """Endpoint should pass query correctly to service"""
    captured_query = {"value": None}

    def mock_get_search_suggestions(query: str):
        captured_query["value"] = query
        return {"suggestions": []}

    monkeypatch.setattr(
        "backend.app.routers.restaurants.get_search_suggestions",
        mock_get_search_suggestions,
    )

    client = TestClient(app)

    client.get("/restaurants/search/suggestions?q=burger")

    assert captured_query["value"] == "burger"
