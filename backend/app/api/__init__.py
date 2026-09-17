from fastapi import APIRouter
from app.api import auth, detection, statistics, health, websocket

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

# Include sub-routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    detection.router,
    prefix="/detection",
    tags=["detection"]
)

api_router.include_router(
    statistics.router,
    prefix="/statistics",
    tags=["statistics"]
)

api_router.include_router(
    websocket.router,
    prefix="/ws",
    tags=["websocket"]
)
