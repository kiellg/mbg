#pylint: disable=ungrouped-imports, wrong-import-position
"""Main FastAPI app"""

from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.restaurants import router as restaurants_router
from app.routers.carts import router as carts_router
from app.routers.orders import router as orders_router
from app.routers.profile import router as profile_router
from app.routers.checkouts import router as checkout_router
from app.routers.payments import router as payment_router
from app.routers.deliveries import router as deliveries_router
from app.routers.notifications import router as notifications_router
from app.routers.recently_viewed import router as recently_viewed_router
from app.routers.reviews import router as reviews_router
from app.routers.favourites import router as favourites_router
from app.routers.coupons import router as coupons_router
from app.routers.admin import router as admin_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1573"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(restaurants_router)
app.include_router(carts_router)
app.include_router(orders_router)
app.include_router(profile_router)
app.include_router(checkout_router)
app.include_router(payment_router)
app.include_router(deliveries_router)
app.include_router(notifications_router)
app.include_router(recently_viewed_router)
app.include_router(reviews_router)
app.include_router(favourites_router)
app.include_router(coupons_router)
app.include_router(admin_router)

@app.get("/health")
def health():
    """Health check"""
    return {"status": "ok"}

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        "main:app",
        host='0.0.0.0',
        port=8000,
        reload=False
    )
