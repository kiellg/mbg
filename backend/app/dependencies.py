"""Shared FastAPI dependencies."""

from fastapi import HTTPException, Header


def get_current_user(fake_user_id: int = Header(...)) -> dict:
    """
    Temporary auth stub — expects fake-user-id header.
    Replace this with real JWT verification when auth is implemented.
    """
    if fake_user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return {"id": fake_user_id}
