from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database.database import Base
import uuid


class Detection(Base):
    __tablename__ = "detections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    label = Column(String, nullable=False)  # "normal" or "abnormal"
    confidence = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source = Column(String, default="camera-01")
    event_id = Column(String, unique=True, nullable=False)
    
    # Additional fields
    frame_data = Column(Text, nullable=True)  # Base64 encoded frame if needed
    keypoints = Column(Text, nullable=True)  # JSON string of keypoints
    extra_metadata = Column("metadata", Text, nullable=True)  # Additional metadata as JSON
    
    # Processing status
    processed = Column(Boolean, default=True)
    processing_time = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<Detection(id={self.id}, label={self.label}, confidence={self.confidence})>"
