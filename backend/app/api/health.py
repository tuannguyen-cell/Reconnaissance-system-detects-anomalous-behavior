import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from fastapi import APIRouter
from app.models.schemas import ServerStatus
from app.services.inference_service import inference_service

router = APIRouter()


@router.get("/status", response_model=ServerStatus)
async def get_server_status():
    """
    Get server and model status
    """
    status_data = inference_service.get_status()
    return ServerStatus(**status_data)


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "service": "behavior-monitor-api",
        "version": "0.1.0"
    }


@router.post("/reset")
async def reset_detection_buffer():
    """
    Reset the detection sequence buffer
    """
    inference_service.reset_buffer()
    return {
        "message": "Detection buffer reset successfully",
        "buffer_size": 0
    }
