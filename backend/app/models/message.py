"""
Message-related Pydantic models.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Message(BaseModel):
    """Message model."""
    id: str
    type: str  # 'text', 'file', 'system'
    content: str
    sender: str
    sender_id: str
    timestamp: datetime
    session_id: str
    fileName: Optional[str] = None
    fileSize: Optional[int] = None
    fileType: Optional[str] = None
    downloadUrl: Optional[str] = None
    fileId: Optional[str] = None

class MessageResponse(BaseModel):
    """Message response model."""
    success: bool
    message: str
    message_id: str

class UserEvent(BaseModel):
    """User event model."""
    type: str  # 'user_joined', 'user_left'
    user_id: str
    user_name: str
    timestamp: datetime
    session_id: str
