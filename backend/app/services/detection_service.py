import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import uuid

from app.models.detection import Detection
from app.models.schemas import DetectionCreate, DetectionFilter, DetectionResponse, Statistics
from app.core.config import settings


class DetectionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_detection(self, detection_data: DetectionCreate) -> Detection:
        """Create a new detection record"""
        detection = Detection(
            label=detection_data.label,
            confidence=detection_data.confidence,
            source=detection_data.source,
            event_id=detection_data.event_id,
            frame_data=detection_data.frame_data,
            keypoints=detection_data.keypoints,
            extra_metadata=detection_data.metadata,
            processed=True,
            processing_time=0.0
        )
        
        self.db.add(detection)
        await self.db.commit()
        await self.db.refresh(detection)
        return detection

    async def get_detection(self, detection_id: str) -> Optional[Detection]:
        """Get a specific detection by ID"""
        result = await self.db.execute(
            select(Detection).where(Detection.id == detection_id)
        )
        return result.scalar_one_or_none()

    async def get_detections(
        self,
        filter: Optional[DetectionFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Detection], int]:
        """Get detections with optional filtering"""
        query = select(Detection)
        
        if filter:
            conditions = []
            if filter.label:
                conditions.append(Detection.label == filter.label)
            if filter.start_date:
                conditions.append(Detection.timestamp >= filter.start_date)
            if filter.end_date:
                conditions.append(Detection.timestamp <= filter.end_date)
            if filter.source:
                conditions.append(Detection.source == filter.source)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(Detection.timestamp.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        detections = result.scalars().all()
        
        return list(detections), total

    async def delete_detection(self, detection_id: str) -> bool:
        """Delete a detection by ID"""
        detection = await self.get_detection(detection_id)
        if detection:
            await self.db.delete(detection)
            await self.db.commit()
            return True
        return False

    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Statistics:
        """Get detection statistics"""
        # Default to last 7 days if no date range provided
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()
        
        # Get total counts
        total_query = select(func.count()).select_from(Detection).where(
            and_(
                Detection.timestamp >= start_date,
                Detection.timestamp <= end_date
            )
        )
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0
        
        # Get normal count
        normal_query = select(func.count()).select_from(Detection).where(
            and_(
                Detection.timestamp >= start_date,
                Detection.timestamp <= end_date,
                Detection.label == "normal"
            )
        )
        normal_result = await self.db.execute(normal_query)
        normal = normal_result.scalar() or 0
        
        # Get abnormal count
        abnormal = total - normal
        
        # Calculate abnormal rate
        abnormal_rate = (abnormal / total * 100) if total > 0 else 0.0
        
        # Get daily data for the last 7 days
        daily_data = []
        for i in range(7):
            day_start = (end_date - timedelta(days=6-i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_total_query = select(func.count()).select_from(Detection).where(
                and_(
                    Detection.timestamp >= day_start,
                    Detection.timestamp < day_end
                )
            )
            day_total_result = await self.db.execute(day_total_query)
            day_total = day_total_result.scalar() or 0
            
            day_normal_query = select(func.count()).select_from(Detection).where(
                and_(
                    Detection.timestamp >= day_start,
                    Detection.timestamp < day_end,
                    Detection.label == "normal"
                )
            )
            day_normal_result = await self.db.execute(day_normal_query)
            day_normal = day_normal_result.scalar() or 0
            
            day_abnormal = day_total - day_normal
            
            daily_data.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "normal": day_normal,
                "abnormal": day_abnormal
            })
        
        return Statistics(
            total=total,
            normal=normal,
            abnormal=abnormal,
            abnormal_rate=abnormal_rate,
            daily_data=daily_data
        )

    async def cleanup_old_detections(self, days: int = 30) -> int:
        """Clean up detections older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        delete_query = select(Detection).where(
            Detection.timestamp < cutoff_date
        )
        result = await self.db.execute(delete_query)
        old_detections = result.scalars().all()
        
        count = len(old_detections)
        for detection in old_detections:
            await self.db.delete(detection)
        
        await self.db.commit()
        return count

    async def get_recent_detections(self, limit: int = 10) -> List[Detection]:
        """Get most recent detections"""
        query = select(Detection).order_by(Detection.timestamp.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
