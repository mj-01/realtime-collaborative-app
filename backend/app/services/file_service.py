"""
File service for handling file operations.
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional
from google.cloud import storage
from google.cloud.exceptions import NotFound
from app.config import settings
from app.models.file import FileMetadata, FileUploadResponse, FileInfo
from app.utils.logging import get_logger

logger = get_logger("file_service")

class FileService:
    """Service for file operations."""
    
    def __init__(self):
        """Initialize file service."""
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(settings.gcs_bucket_name)
        logger.info(f"File service initialized with bucket: {settings.gcs_bucket_name}")
    
    async def upload_file(self, file_content: bytes, filename: str, content_type: str) -> FileUploadResponse:
        """Upload a file to Google Cloud Storage."""
        try:
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create blob in bucket
            blob = self.bucket.blob(unique_filename)
            blob.content_type = content_type or 'application/octet-stream'
            
            # Upload file
            blob.upload_from_string(file_content, content_type=blob.content_type)
            
            # Make blob public and get public URL
            blob.make_public()
            public_url = blob.public_url
            
            # Create file metadata
            file_metadata = FileMetadata(
                original_name=filename,
                unique_name=unique_filename,
                content_type=blob.content_type,
                size=len(file_content),
                upload_time=datetime.utcnow(),
                public_url=public_url,
                bucket_name=settings.gcs_bucket_name
            )
            
            logger.info(f"File uploaded successfully: {filename} -> {unique_filename}")
            
            return FileUploadResponse(
                success=True,
                file_id="",  # Will be set by caller
                original_name=filename,
                content_type=blob.content_type,
                size=len(file_content),
                download_url=public_url,
                expires_at=(datetime.utcnow() + timedelta(hours=24)).isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error uploading file {filename}: {str(e)}")
            raise
    
    async def delete_file(self, unique_name: str) -> bool:
        """Delete a file from Google Cloud Storage."""
        try:
            blob = self.bucket.blob(unique_name)
            if blob.exists():
                blob.delete()
                logger.info(f"File deleted from Cloud Storage: {unique_name}")
                return True
            else:
                logger.warning(f"File not found in Cloud Storage: {unique_name}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {unique_name}: {str(e)}")
            return False
    
    async def get_file_info(self, unique_name: str) -> Optional[FileInfo]:
        """Get file information."""
        try:
            blob = self.bucket.blob(unique_name)
            if not blob.exists():
                return None
            
            public_url = blob.public_url
            expiration_time = datetime.utcnow() + timedelta(hours=24)
            
            return FileInfo(
                file_id="",  # Will be set by caller
                original_name=blob.name,
                content_type=blob.content_type,
                size=blob.size,
                upload_time=blob.time_created.isoformat(),
                download_url=public_url,
                expires_at=expiration_time.isoformat()
            )
        except Exception as e:
            logger.error(f"Error getting file info for {unique_name}: {str(e)}")
            return None
