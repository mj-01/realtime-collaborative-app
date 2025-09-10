"""
Firestore service for database operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import firestore
from app.config import settings
from app.models.file import FileMetadata, BulkDeleteRequest
from app.models.message import Message, UserEvent
from app.utils.logging import get_logger

logger = get_logger("firestore_service")

class FirestoreService:
    """Service for Firestore operations."""
    
    def __init__(self):
        """Initialize Firestore service."""
        self.db = firestore.Client()
        logger.info("Firestore service initialized")
    
    async def save_file_metadata(self, file_metadata: FileMetadata) -> str:
        """Save file metadata to Firestore."""
        try:
            doc_ref = self.db.collection('uploaded_files').add(file_metadata.dict())
            file_id = doc_ref[1].id
            logger.info(f"File metadata saved with ID: {file_id}")
            return file_id
        except Exception as e:
            logger.error(f"Error saving file metadata: {str(e)}")
            raise
    
    async def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file metadata by ID."""
        try:
            doc_ref = self.db.collection('uploaded_files').document(file_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting file metadata for {file_id}: {str(e)}")
            return None
    
    async def delete_file_metadata(self, file_id: str) -> bool:
        """Delete file metadata."""
        try:
            self.db.collection('uploaded_files').document(file_id).delete()
            logger.info(f"File metadata deleted: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file metadata {file_id}: {str(e)}")
            return False
    
    async def save_message(self, message: Message) -> bool:
        """Save message to Firestore."""
        try:
            self.db.collection('messages').add(message.dict())
            logger.info(f"Message saved from {message.sender}: {message.content[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            return False
    
    async def get_recent_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent messages."""
        try:
            messages_query = self.db.collection('messages').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            messages = []
            
            for doc in messages_query.stream():
                msg_data = doc.to_dict()
                # Convert Firestore timestamp to milliseconds for frontend
                if 'timestamp' in msg_data:
                    msg_data['timestamp'] = int(msg_data['timestamp'].timestamp() * 1000)
                messages.append(msg_data)
            
            logger.info(f"Retrieved {len(messages)} recent messages")
            return list(reversed(messages))
        except Exception as e:
            logger.error(f"Error getting recent messages: {str(e)}")
            return []
    
    async def delete_message(self, message_id: str) -> bool:
        """Delete message by ID."""
        try:
            self.db.collection('messages').document(message_id).delete()
            logger.info(f"Message deleted: {message_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting message {message_id}: {str(e)}")
            return False
    
    async def delete_file_messages(self, file_id: str) -> int:
        """Delete all messages associated with a file."""
        try:
            messages_query = self.db.collection('messages').where('type', '==', 'file').where('fileId', '==', file_id)
            deleted_count = 0
            
            for message_doc in messages_query.stream():
                message_doc.reference.delete()
                deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} file messages for file {file_id}")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting file messages for {file_id}: {str(e)}")
            return 0
    
    async def save_user_event(self, event: UserEvent) -> bool:
        """Save user event."""
        try:
            self.db.collection('chat_events').add(event.dict())
            logger.info(f"User event saved: {event.type} - {event.user_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving user event: {str(e)}")
            return False
    
    async def bulk_delete_files(self, request: BulkDeleteRequest) -> Dict[str, int]:
        """Bulk delete files based on criteria."""
        try:
            deleted_files = 0
            deleted_messages = 0
            
            # Build query for uploaded_files
            files_query = self.db.collection('uploaded_files')
            
            # Apply filters
            if request.start_date and request.end_date:
                start_dt = datetime.fromisoformat(request.start_date)
                end_dt = datetime.fromisoformat(request.end_date)
                files_query = files_query.where('upload_time', '>=', start_dt).where('upload_time', '<=', end_dt)
            
            if request.file_types:
                files_query = files_query.where('content_type', 'in', request.file_types)
            
            # Execute query and delete files
            files_docs = files_query.stream()
            
            for file_doc in files_docs:
                file_data = file_doc.to_dict()
                
                # Apply filename pattern filter if specified
                if request.filename_pattern and request.filename_pattern.lower() not in file_data['original_name'].lower():
                    continue
                
                # Delete file messages
                messages_deleted = await self.delete_file_messages(file_doc.id)
                deleted_messages += messages_deleted
                
                # Delete file metadata
                file_doc.reference.delete()
                deleted_files += 1
            
            logger.info(f"Bulk delete completed: {deleted_files} files, {deleted_messages} messages")
            return {
                "deleted_files": deleted_files,
                "deleted_messages": deleted_messages,
                "total_deleted": deleted_files + deleted_messages
            }
        except Exception as e:
            logger.error(f"Error in bulk delete: {str(e)}")
            return {"deleted_files": 0, "deleted_messages": 0, "total_deleted": 0}
