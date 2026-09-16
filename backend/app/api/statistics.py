import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.database.database import get_db
from app.models.schemas import Statistics
from app.services.detection_service import DetectionService
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("/statistics", response_model=Statistics)
async def get_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detection statistics
    """
    try:
        # Parse dates if provided
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            parsed_start_date = datetime.fromisoformat(start_date)
        if end_date:
            parsed_end_date = datetime.fromisoformat(end_date)
        
        detection_service = DetectionService(db)
        statistics = await detection_service.get_statistics(
            start_date=parsed_start_date,
            end_date=parsed_end_date
        )
        
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/summary")
async def get_summary(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get quick summary statistics
    """
    try:
        detection_service = DetectionService(db)
        statistics = await detection_service.get_statistics()
        
        return {
            "total_detections": statistics.total,
            "normal_count": statistics.normal,
            "abnormal_count": statistics.abnormal,
            "abnormal_rate": statistics.abnormal_rate,
            "recent_abnormal": statistics.daily_data[-1]["abnormal"] if statistics.daily_data else 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        )
