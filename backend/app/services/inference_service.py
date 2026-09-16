import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import torch
import torch.nn as nn
import numpy as np
import cv2
import base64
from pathlib import Path
from typing import Tuple, Optional, Dict
from collections import deque
import time
import logging
from ultralytics import YOLO

from app.core.config import settings

logger = logging.getLogger(__name__)


# LSTM Model Architecture (same as training script)
class LSTMAnomalyDetector(nn.Module):
    def __init__(self, input_size=51, hidden_size=128, num_layers=2, num_classes=2, dropout=0.3):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size, hidden_size=hidden_size,
            num_layers=num_layers, batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.head = nn.Sequential(
            nn.LayerNorm(hidden_size),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :])


class InferenceService:
    def __init__(self):
        self.yolo_model = None
        self.lstm_model = None
        self.device = torch.device(settings.DEVICE)
        self.sequence_buffer = deque(maxlen=settings.SEQUENCE_LENGTH)
        self.is_loaded = False
        self.load_time = 0
        self.start_time = time.time()
        
    def load_models(self):
        """Load YOLO and LSTM models"""
        try:
            logger.info(f"Loading models on device: {self.device}")
            
            # Load YOLO model
            yolo_path = Path(settings.YOLO_MODEL_PATH)
            if not yolo_path.exists():
                # Try relative path from backend directory
                yolo_path = Path("../yolov8n-pose.pt")
            
            logger.info(f"Loading YOLO model from: {yolo_path}")
            self.yolo_model = YOLO(str(yolo_path))
            
            # Load LSTM model
            lstm_path = Path(settings.LSTM_MODEL_PATH)
            if not lstm_path.exists():
                lstm_path = Path("../models/lstm_best.pt")
            
            logger.info(f"Loading LSTM model from: {lstm_path}")
            if lstm_path.exists():
                checkpoint = torch.load(lstm_path, map_location=self.device, weights_only=False)
                self.lstm_model = LSTMAnomalyDetector(
                    input_size=checkpoint.get("input_size", settings.INPUT_SIZE),
                    hidden_size=checkpoint.get("hidden_size", 128),
                    num_layers=checkpoint.get("num_layers", 2),
                    num_classes=checkpoint.get("num_classes", 2),
                ).to(self.device)
                self.lstm_model.load_state_dict(checkpoint["model_state"])
                self.lstm_model.eval()
                logger.info(f"LSTM model loaded successfully. Val Acc: {checkpoint.get('val_acc', 0):.2%}")
            else:
                logger.warning(f"LSTM model not found at {lstm_path}. Will use YOLO-only mode.")
            
            self.is_loaded = True
            self.load_time = time.time() - self.start_time
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.is_loaded = False
            raise

    def decode_base64_image(self, base64_string: str) -> np.ndarray:
        """Decode base64 image to numpy array"""
        try:
            # Remove data URL prefix if present
            if "base64," in base64_string:
                base64_string = base64_string.split("base64,")[1]
            
            image_data = base64.b64decode(base64_string)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return image
        except Exception as e:
            logger.error(f"Error decoding base64 image: {e}")
            raise ValueError("Invalid base64 image data")

    def extract_keypoints(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """Extract pose keypoints using YOLO"""
        try:
            results = self.yolo_model(image, verbose=False, device=self.device, conf=settings.CONFIDENCE_THRESHOLD)
            result = results[0]
            
            pose_vector = np.zeros(settings.INPUT_SIZE, dtype=np.float32)
            n_persons = 0
            
            if result.keypoints is not None and len(result.keypoints) > 0:
                n_persons = len(result.keypoints)
                
                # Select person with largest bounding box (main person)
                if result.boxes is not None and len(result.boxes) > 0:
                    areas = []
                    for i in range(n_persons):
                        box = result.boxes.xyxy[i].cpu().numpy()
                        areas.append((box[2]-box[0]) * (box[3]-box[1]))
                    main_idx = int(np.argmax(areas))
                    
                    kp_xy = result.keypoints.xy[main_idx]
                    kp_conf = result.keypoints.conf[main_idx]
                    
                    # Normalize and flatten
                    h, w = image.shape[:2]
                    xy_np = kp_xy.cpu().numpy().copy()
                    xy_np[:, 0] /= w
                    xy_np[:, 1] /= h
                    c_np = kp_conf.cpu().numpy()
                    
                    # Valid person if has clear keypoints
                    if len(c_np) > 0 and (np.mean(c_np) > 0.15 or np.max(c_np) > 0.35):
                        pose_vector = np.concatenate([xy_np.flatten(), c_np])
            
            return pose_vector, n_persons
            
        except Exception as e:
            logger.error(f"Error extracting keypoints: {e}")
            return np.zeros(settings.INPUT_SIZE, dtype=np.float32), 0

    def detect_anomaly(self, frame_data: str, threshold: float = 0.6) -> Dict:
        """
        Main detection function
        Returns: detection result with label, confidence, etc.
        """
        start_time = time.time()
        
        try:
            # Decode image
            image = self.decode_base64_image(frame_data)
            
            # Extract keypoints
            pose_vector, n_persons = self.extract_keypoints(image)
            
            # Add to sequence buffer
            self.sequence_buffer.append(pose_vector)
            
            # Default result
            result = {
                "label": "normal",
                "confidence": 0.5,
                "n_persons": n_persons,
                "buffer_size": len(self.sequence_buffer),
                "processing_time": time.time() - start_time,
                "model_used": "yolo_only"
            }
            
            # LSTM inference if buffer is full and model is loaded
            if len(self.sequence_buffer) == settings.SEQUENCE_LENGTH and self.lstm_model is not None:
                with torch.no_grad():
                    seq = np.array(self.sequence_buffer, dtype=np.float32)
                    X = torch.tensor(seq).unsqueeze(0).to(self.device)
                    logits = self.lstm_model(X)
                    probs = torch.softmax(logits, dim=1)[0]
                    prob_abnormal = float(probs[1])
                    
                    result["label"] = "abnormal" if prob_abnormal >= threshold else "normal"
                    result["confidence"] = prob_abnormal
                    result["model_used"] = "yolo_lstm"
            
            result["processing_time"] = time.time() - start_time
            return result
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return {
                "label": "normal",
                "confidence": 0.0,
                "n_persons": 0,
                "buffer_size": len(self.sequence_buffer),
                "processing_time": time.time() - start_time,
                "model_used": "error",
                "error": str(e)
            }

    def get_status(self) -> Dict:
        """Get service status"""
        return {
            "status": "ok" if self.is_loaded else "error",
            "model_loaded": self.is_loaded,
            "model_name": "lstm_best.pt" if self.lstm_model else "yolo_only",
            "model_version": "1.0.0",
            "device": str(self.device),
            "uptime": time.time() - self.start_time,
            "load_time": self.load_time,
            "buffer_size": len(self.sequence_buffer),
            "sequence_length": settings.SEQUENCE_LENGTH
        }

    def reset_buffer(self):
        """Reset the sequence buffer"""
        self.sequence_buffer.clear()


# Global inference service instance
inference_service = InferenceService()
