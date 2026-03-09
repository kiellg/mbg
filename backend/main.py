"""Main FastAPI app"""

from fastapi import FastAPI
from backend.app.routers.auth import router as auth_router
from backend.app.routers.restaurants import router as restaurants_router
from backend.app.routers.carts import router as carts_router
from backend.app.routers.orders import router as orders_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(restaurants_router)
app.include_router(carts_router)
app.include_router(orders_router)

@app.get("/health")
def health():
    """Health check"""
    return {"status": "ok"}
