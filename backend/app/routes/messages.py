"""
Message-related API routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from app.models.message import MessageResponse
from app.services.firestore_service import FirestoreService
from app.services.file_service import FileService
from app.utils.logging import get_logger

logger = get_logger("messages_routes")
router = APIRouter(prefix="/messages", tags=["messages"])

def get_firestore_service() -> FirestoreService:
    return FirestoreService()

def get_file_service() -> FileService:
    return FileService()

@router.delete("/{message_id}", response_model=MessageResponse)
async def delete_message(
    message_id: str,
    firestore_service: FirestoreService = Depends(get_firestore_service),
    file_service: FileService = Depends(get_file_service)
):
    """Delete a message from Firestore."""
    try:
        # Get message from Firestore
        message_data = await firestore_service.get_file_metadata(message_id)  # This should be get_message_metadata
        
        if not message_data:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # If it's a file message, also delete the associated file
        if message_data.get('type') == 'file' and 'fileId' in message_data:
            try:
                # Delete the file as well
                file_deleted = await file_service.delete_file(message_data['fileId'])
                if file_deleted:
                    logger.info(f"Associated file deleted: {message_data['fileId']}")
            except Exception as e:
                logger.warning(f"Error deleting associated file: {str(e)}")
                # Continue with message deletion even if file deletion fails
        
        # Delete the message
        message_deleted = await firestore_service.delete_message(message_id)
        
        if not message_deleted:
            raise HTTPException(status_code=500, detail="Failed to delete message")
        
        logger.info(f"Message deleted: {message_id}")
        
        return MessageResponse(
            success=True,
            message="Message deleted successfully",
            message_id=message_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message {message_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")
