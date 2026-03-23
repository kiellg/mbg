"""Tests for recently viewed items"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_recently_viewed_empty(monkeypatch):
    """Should return empty list when user has no history"""

    def mock_get_session(token):
        return {"user_id": "user_1"}

    monkeypatch.setattr(
        "backend.app.routers.recently_viewed.get_session",
        mock_get_session,
    )

    response = client.get("/recently-viewed")

    assert response.status_code == 200
    assert response.json() == {"items": []}

def test_recently_viewed_after_tracking(monkeypatch):
    """Items should appear after being tracked"""

    def mock_get_session(token):
        return {"user_id": "user_1"}

    monkeypatch.setattr(
        "backend.app.routers.recently_viewed.get_session",
        mock_get_session,
    )

    from backend.app.services.recently_viewed_service import track_recently_viewed

    track_recently_viewed("user_1", "restaurant", 1)

    response = client.get("/recently-viewed")

    assert response.status_code == 200
    data = response.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["type"] == "restaurant"
    assert data["items"][0]["id"] == 1

def test_recently_viewed_order_and_no_duplicates(monkeypatch):
    """Most recent item should appear fisrt and duplicates removed"""

    def mock_get_session(token):
        return {"user_id": "user_1"}

    monkeypatch.setattr(
        "backend.app.routers.recently_viewed.get_session",
        mock_get_session,
    )

    from backend.app.services.recently_viewed_service import track_recently_viewed

    track_recently_viewed("user_1", "restaurant", 1)
    track_recently_viewed("user_1", "restaurant", 2)
    track_recently_viewed("user_1", "restaurant", 1)

    response = client.get("/recently-viewed")

    data = response.json()["items"]

    assert data[0]["id"] == 1
    assert data[1]["id"] == 2

    assert len(data) == 2

def test_recently_viewed_max_limit(monkeypatch):
    """Should keep only the 10 most recent items"""

    def mock_get_session(token):
        return {"user_id": "user_1"}

    monkeypatch.setattr(
        "backend.app.routers.recently_viewed.get_session",
        mock_get_session,
    )

    from backend.app.services.recently_viewed_service import track_recently_viewed

    for i in range(12):
        track_recently_viewed("user_1", "restaurant", i)

    response = client.get("/recently-viewed")

    data = response.json()["items"]

    assert len(data) == 10

    assert data[0]["id"] == 11

    assert data[-1]["id"] == 2

def test_recently_viewed_no_session():
    """Should return empty list if user is not authenticated"""

    response = client.get("/recently-viewed")

    assert response.status_code == 200
    assert response.json() == {"items": []}
