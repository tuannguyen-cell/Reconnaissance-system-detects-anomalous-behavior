import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
from datetime import datetime

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Connection might be closed
                pass


manager = ConnectionManager()


@router.websocket("/detection")
async def websocket_detection(websocket: WebSocket):
    """
    WebSocket endpoint for real-time detection updates
    """
    await manager.connect(websocket)
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to detection stream",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                elif message.get("type") == "subscribe":
                    # Handle subscription to specific events
                    await websocket.send_json({
                        "type": "subscribed",
                        "channels": message.get("channels", []),
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client disconnected from detection stream")


@router.websocket("/statistics")
async def websocket_statistics(websocket: WebSocket):
    """
    WebSocket endpoint for real-time statistics updates
    """
    await manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to statistics stream",
            "timestamp": datetime.now().isoformat()
        })
        
        # Send periodic statistics updates
        while True:
            # This would typically fetch real statistics from database
            await asyncio.sleep(5)  # Update every 5 seconds
            
            # Mock statistics update
            await websocket.send_json({
                "type": "statistics_update",
                "data": {
                    "timestamp": datetime.now().isoformat(),
                    "total_detections": 0,
                    "abnormal_count": 0,
                    "normal_count": 0
                }
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client disconnected from statistics stream")


# Helper function to broadcast detection results
async def broadcast_detection(detection_data: dict):
    """
    Broadcast detection results to all connected clients
    """
    message = {
        "type": "detection",
        "data": detection_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)
