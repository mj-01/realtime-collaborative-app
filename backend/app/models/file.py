"""
File-related Pydantic models.
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class FileMetadata(BaseModel):
    """File metadata model."""
    original_name: str
    unique_name: str
    content_type: str
    size: int
    upload_time: datetime
    public_url: str
    bucket_name: str
    file_id: Optional[str] = None
    
    @field_validator('size')
    @classmethod
    def validate_size(cls, v):
        if v <= 0:
            raise ValueError('File size must be positive')
        return v

class FileUploadResponse(BaseModel):
    """File upload response model."""
    success: bool
    file_id: str
    original_name: str
    content_type: str
    size: int
    download_url: str
    expires_at: str

class FileInfo(BaseModel):
    """File information model."""
    file_id: str
    original_name: str
    content_type: str
    size: int
    upload_time: str
    download_url: str
    expires_at: str

class BulkDeleteRequest(BaseModel):
    """Bulk delete request model."""
    sender_name: Optional[str] = None
    filename_pattern: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    file_types: Optional[list] = None

class BulkDeleteResponse(BaseModel):
    """Bulk delete response model."""
    success: bool
    message: str
    deleted_files: int
    deleted_messages: int
    total_deleted: int
