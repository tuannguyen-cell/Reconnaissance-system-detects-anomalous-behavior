import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.database import get_db
from app.models.schemas import (
    DetectionRequest, DetectionResponseAPI, DetectionResponse,
    DetectionList, DetectionFilter, DetectionCreate
)
from app.services.detection_service import DetectionService
from app.services.inference_service import inference_service
from app.api.deps import get_current_active_user
from app.api.websocket import broadcast_detection

router = APIRouter()


@router.post("/detect", response_model=DetectionResponseAPI)
async def detect_behavior(
    request: DetectionRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Detect behavior from frame data
    """
    try:
        # Perform inference
        result = inference_service.detect_anomaly(
            frame_data=request.frame_data,
            threshold=request.threshold
        )
        
        # Generate event ID
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        
        # Create detection record
        detection_data = DetectionCreate(
            label=result["label"],
            confidence=result["confidence"],
            source=request.source,
            event_id=event_id,
            frame_data=request.frame_data,
            metadata=str(result)
        )
        
        detection_service = DetectionService(db)
        detection = await detection_service.create_detection(detection_data)
        
        response = DetectionResponseAPI(
            label=result["label"],
            confidence=result["confidence"],
            timestamp=detection.timestamp.isoformat(),
            source=request.source,
            event_id=event_id,
            processing_time=result["processing_time"]
        )

        if result["label"] == "abnormal":
            await broadcast_detection({
                "label": response.label,
                "confidence": response.confidence,
                "timestamp": response.timestamp,
                "source": response.source,
                "event_id": response.event_id,
                "processing_time": response.processing_time,
            })

        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Detection failed"
        )


@router.get("/detections", response_model=DetectionList)
async def get_detections(
    label: str = None,
    start_date: str = None,
    end_date: str = None,
    source: str = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detection history with optional filtering
    """
    try:
        from datetime import datetime
        
        # Build filter
        detection_filter = DetectionFilter()
        if label:
            detection_filter.label = label
        if start_date:
            detection_filter.start_date = datetime.fromisoformat(start_date)
        if end_date:
            detection_filter.end_date = datetime.fromisoformat(end_date)
        if source:
            detection_filter.source = source
        
        detection_service = DetectionService(db)
        detections, total = await detection_service.get_detections(
            filter=detection_filter,
            skip=skip,
            limit=limit
        )
        
        return DetectionList(
            detections=[DetectionResponse.model_validate(d) for d in detections],
            total=total,
            page=skip // limit + 1,
            page_size=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get detections: {str(e)}"
        )


@router.get("/detections/{detection_id}", response_model=DetectionResponse)
async def get_detection(
    detection_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific detection by ID
    """
    detection_service = DetectionService(db)
    detection = await detection_service.get_detection(detection_id)
    
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found"
        )
    
    return DetectionResponse.model_validate(detection)


@router.delete("/detections/{detection_id}")
async def delete_detection(
    detection_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a detection by ID
    """
    detection_service = DetectionService(db)
    success = await detection_service.delete_detection(detection_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found"
        )
    
    return {"message": "Detection deleted successfully"}


@router.get("/recent")
async def get_recent_detections(
    limit: int = 10,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get most recent detections
    """
    detection_service = DetectionService(db)
    detections = await detection_service.get_recent_detections(limit=limit)
    
    return {
        "detections": [DetectionResponse.model_validate(d) for d in detections],
        "count": len(detections)
    }
