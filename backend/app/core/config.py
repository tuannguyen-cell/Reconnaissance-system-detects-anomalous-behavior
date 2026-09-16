from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Behavior Monitor API"
    VERSION: str = "0.1.0"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./behavior_monitor.db"
    
    # Model Settings
    YOLO_MODEL_PATH: str = str(PROJECT_ROOT / "yolov8n-pose.pt")
    LSTM_MODEL_PATH: str = str(PROJECT_ROOT / "models" / "lstm_best.pt")
    SEQUENCE_LENGTH: int = 30
    INPUT_SIZE: int = 51  # 17 keypoints x (x, y, conf)
    ANOMALY_THRESHOLD: float = 0.6
    
    # Device Settings
    DEVICE: str = "cuda"  # Will be set based on availability
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    # Detection Settings
    MAX_DETECTION_HISTORY: int = 1000
    CONFIDENCE_THRESHOLD: float = 0.25
    
    # WebSocket Settings
    WS_HEARTBEAT_INTERVAL: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Update device based on availability
try:
    import torch
    settings.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError:
    settings.DEVICE = "cpu"
