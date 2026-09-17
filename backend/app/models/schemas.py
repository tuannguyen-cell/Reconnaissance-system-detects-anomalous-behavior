from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DetectionResult(str, Enum):
    NORMAL = "normal"
    ABNORMAL = "abnormal"


class DetectionBase(BaseModel):
    label: DetectionResult
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str = "camera-01"
    event_id: str


class DetectionCreate(DetectionBase):
    frame_data: Optional[str] = None
    keypoints: Optional[str] = None
    metadata: Optional[str] = None


class DetectionResponse(DetectionBase):
    id: str
    timestamp: datetime
    processed: bool
    processing_time: Optional[float] = None
    
    class Config:
        from_attributes = True


class DetectionList(BaseModel):
    detections: List[DetectionResponse]
    total: int
    page: int
    page_size: int


class DetectionFilter(BaseModel):
    label: Optional[DetectionResult] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source: Optional[str] = None


class ServerStatus(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str = "ok"
    model_loaded: bool = True
    model_name: str = "lstm_best.pt"
    model_version: str = "1.0.0"
    device: str = "cpu"
    uptime: float = 0.0


class Statistics(BaseModel):
    total: int
    normal: int
    abnormal: int
    abnormal_rate: float
    daily_data: List[dict]


class DetectionRequest(BaseModel):
    frame_data: str  # Base64 encoded image
    threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    source: str = "camera-01"


class DetectionResponseAPI(BaseModel):
    label: DetectionResult
    confidence: float
    timestamp: str
    source: str
    event_id: str
    processing_time: float


class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
