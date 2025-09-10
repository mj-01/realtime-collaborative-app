"""
File-related API routes.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import List
from app.config import settings
from app.models.file import FileUploadResponse, FileInfo, BulkDeleteRequest, BulkDeleteResponse
from app.services.file_service import FileService
from app.services.firestore_service import FirestoreService
from app.utils.logging import get_logger

logger = get_logger("files_routes")
router = APIRouter(prefix="/files", tags=["files"])

# Dependency injection
def get_file_service() -> FileService:
    return FileService()

def get_firestore_service() -> FirestoreService:
    return FirestoreService()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Upload a file to Google Cloud Storage and return a signed download URL."""
    
    # Check if file upload is enabled
    if not settings.enable_file_upload:
        raise HTTPException(status_code=403, detail="File upload is disabled")
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail=f"File size exceeds {settings.max_file_size_mb}MB limit"
        )
    
    try:
        # Upload file to storage
        upload_response = await file_service.upload_file(
            file_content, file.filename, file.content_type
        )
        
        # Save metadata to Firestore
        from app.models.file import FileMetadata
        from datetime import datetime
        file_metadata = FileMetadata(
            original_name=file.filename,
            unique_name=upload_response.file_id,  # This will be set by the service
            content_type=file.content_type,
            size=len(file_content),
            upload_time=datetime.utcnow(),
            public_url=upload_response.download_url,
            bucket_name=settings.gcs_bucket_name
        )
        
        file_id = await firestore_service.save_file_metadata(file_metadata)
        upload_response.file_id = file_id
        
        logger.info(f"File uploaded successfully: {file.filename} (ID: {file_id})")
        return upload_response
        
    except Exception as e:
        logger.error(f"Error uploading file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.get("/{file_id}", response_model=FileInfo)
async def get_file_info(
    file_id: str,
    file_service: FileService = Depends(get_file_service),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Get file information and generate new signed URL."""
    try:
        # Get file metadata from Firestore
        file_data = await firestore_service.get_file_metadata(file_id)
        
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get file info from storage
        file_info = await file_service.get_file_info(file_data['unique_name'])
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found in storage")
        
        file_info.file_id = file_id
        file_info.original_name = file_data['original_name']
        
        logger.info(f"File info retrieved: {file_id}")
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {str(e)}")

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    file_service: FileService = Depends(get_file_service),
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Delete a file from both Cloud Storage and Firestore."""
    try:
        # Get file metadata from Firestore
        file_data = await firestore_service.get_file_metadata(file_id)
        
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete from Cloud Storage
        storage_deleted = await file_service.delete_file(file_data['unique_name'])
        
        # Delete from Firestore
        firestore_deleted = await firestore_service.delete_file_metadata(file_id)
        
        # Delete associated messages
        messages_deleted = await firestore_service.delete_file_messages(file_id)
        
        logger.info(f"File deleted: {file_id} (storage: {storage_deleted}, firestore: {firestore_deleted}, messages: {messages_deleted})")
        
        return {
            "success": True,
            "message": f"File '{file_data['original_name']}' deleted successfully",
            "file_id": file_id,
            "original_name": file_data['original_name']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_files(
    request: BulkDeleteRequest,
    firestore_service: FirestoreService = Depends(get_firestore_service)
):
    """Bulk delete files based on criteria."""
    try:
        result = await firestore_service.bulk_delete_files(request)
        
        logger.info(f"Bulk delete completed: {result['total_deleted']} items deleted")
        
        return BulkDeleteResponse(
            success=True,
            message="Bulk delete completed successfully",
            deleted_files=result["deleted_files"],
            deleted_messages=result["deleted_messages"],
            total_deleted=result["total_deleted"]
        )
        
    except Exception as e:
        logger.error(f"Error in bulk delete: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to bulk delete files: {str(e)}")
