from fastapi import APIRouter
from app.api import detection, statistics, health, websocket

api_router = APIRouter()

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
