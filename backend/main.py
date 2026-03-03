"""Main FastAPI app"""

from fastapi import FastAPI
from backend.app.routers.restaurants import router as restaurants_router

app = FastAPI()
app.include_router(restaurants_router)

@app.get("/health")
def health():
    """Health check"""
    return {"status": "ok"}
