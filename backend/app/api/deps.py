from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from typing import Optional

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[dict]:
    """
    Get current user from JWT token
    For MVP, we'll skip authentication and return a mock user
    """
    # TODO: Implement proper JWT authentication
    # For MVP, return a mock user
    return {
        "id": "mock_user_id",
        "username": "demo_user",
        "email": "demo@example.com",
        "is_active": True,
        "is_superuser": False
    }


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get current active user"""
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user
