"""Router for recently viewed items"""

from typing import Optional
from fastapi import APIRouter, Request, Header

from app.services.recently_viewed_service import get_recent_items
from app.schemas.recently_viewed import RecentlyViewedResponse
from app.repositories.session_repo import get_session

router = APIRouter(tags=["recently_viewed"])

def get_session_token(
        request: Request,
        session_token: Optional[str] = Header(default=None),
) -> Optional[str]:
    """Return session token from header or cookie"""
    if session_token:
        return session_token
    return request.cookies.get("session_token")

@router.get("/recently-viewed", response_model=RecentlyViewedResponse)
def read_recently_viewed(
    request: Request,
    session_token: Optional[str] = Header(default=None),
):
    """Return recently viewed items for current user"""
    token = get_session_token(request, session_token)
    session = get_session(token)

    if not session:
        return {"items": []}

    items = get_recent_items(session["user_id"])
    return {"items": items}
