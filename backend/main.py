from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import socketio
from fastapi_socketio import SocketManager
from google.cloud import firestore, storage
from google.cloud.exceptions import NotFound
import json
import uuid
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# CORS configuration
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,https://frontend-987275518911.us-central1.run.app').split(',')

app = FastAPI(title="Backend API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Socket.IO
sio = socketio.AsyncServer(
    cors_allowed_origins=CORS_ORIGINS,
    async_mode='asgi'
)
socket_manager = SocketManager(app=app, socketio_server=sio)

# Initialize Firestore and Cloud Storage
# Try to use service account key from environment variable first
service_account_key = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
if service_account_key:
    import json
    from google.oauth2 import service_account
    try:
        credentials_info = json.loads(service_account_key)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        db = firestore.Client(credentials=credentials)
        storage_client = storage.Client(credentials=credentials)
        print("Using service account credentials from environment variable")
    except Exception as e:
        print(f"Error parsing service account key: {e}")
        # Fallback to default credentials
        db = firestore.Client()
        storage_client = storage.Client()
else:
    # Use default credentials (works in Cloud Run)
    db = firestore.Client()
    storage_client = storage.Client()
    print("Using default credentials")

# Cloud Storage configuration
BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'labs-realtime-app-files')
bucket = storage_client.bucket(BUCKET_NAME)

# File upload configuration
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 10))
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
ALLOWED_FILE_TYPES = os.getenv('ALLOWED_FILE_TYPES', 'image/*,application/pdf,text/*,application/json').split(',')

# Feature flags
ENABLE_FILE_UPLOAD = os.getenv('ENABLE_FILE_UPLOAD', 'true').lower() == 'true'
ENABLE_REAL_TIME_CHAT = os.getenv('ENABLE_REAL_TIME_CHAT', 'true').lower() == 'true'
ENABLE_WHITEBOARD = os.getenv('ENABLE_WHITEBOARD', 'true').lower() == 'true'
ENABLE_FILE_CLEANUP = os.getenv('ENABLE_FILE_CLEANUP', 'true').lower() == 'true'

# Pydantic models
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

# In-memory storage (replace with database in production)
items_db = []
next_id = 1

@app.get("/")
async def root():
    return {"message": "Welcome to the Backend API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/items", response_model=List[Item])
async def get_items():
    return items_db

@app.post("/items", response_model=Item)
async def create_item(item: ItemCreate):
    global next_id
    new_item = Item(
        id=next_id,
        name=item.name,
        description=item.description,
        price=item.price
    )
    items_db.append(new_item)
    next_id += 1
    return new_item

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    return {"error": "Item not found"}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    global items_db
    items_db = [item for item in items_db if item.id != item_id]
    return {"message": "Item deleted successfully"}

# File upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to Google Cloud Storage and return a signed download URL"""
    
    # Check if file upload is enabled
    if not ENABLE_FILE_UPLOAD:
        raise HTTPException(status_code=403, detail="File upload is disabled")
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds {MAX_FILE_SIZE_MB}MB limit")
    
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create blob in bucket
        blob = bucket.blob(unique_filename)
        
        # Set content type
        blob.content_type = file.content_type or 'application/octet-stream'
        
        # Upload file
        blob.upload_from_string(file_content, content_type=blob.content_type)
        
        # Make blob public and get public URL
        blob.make_public()
        public_url = blob.public_url
        
        # For now, use public URL instead of signed URL
        # TODO: Implement proper signed URLs with service account
        expiration_time = datetime.utcnow() + timedelta(hours=24)  # Longer expiration for public URLs
        
        # Save file metadata to Firestore
        file_metadata = {
            'original_name': file.filename,
            'unique_name': unique_filename,
            'content_type': blob.content_type,
            'size': len(file_content),
            'upload_time': datetime.utcnow(),
            'public_url': public_url,
            'bucket_name': BUCKET_NAME
        }
        
        # Save to Firestore
        doc_ref = db.collection('uploaded_files').add(file_metadata)
        
        return {
            "success": True,
            "file_id": doc_ref[1].id,
            "original_name": file.filename,
            "unique_name": unique_filename,
            "content_type": blob.content_type,
            "size": len(file_content),
            "download_url": public_url,
            "expires_at": expiration_time.isoformat()
        }
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@app.get("/files/{file_id}")
async def get_file_info(file_id: str):
    """Get file information and generate new signed URL"""
    try:
        # Get file metadata from Firestore
        doc_ref = db.collection('uploaded_files').document(file_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_data = doc.to_dict()
        
        # Get public URL (files are now public)
        blob = bucket.blob(file_data['unique_name'])
        public_url = blob.public_url
        expiration_time = datetime.utcnow() + timedelta(hours=24)
        
        # Update last accessed time in Firestore
        doc_ref.update({
            'last_accessed': datetime.utcnow()
        })
        
        return {
            "file_id": file_id,
            "original_name": file_data['original_name'],
            "content_type": file_data['content_type'],
            "size": file_data['size'],
            "upload_time": file_data['upload_time'].isoformat(),
            "download_url": public_url,
            "expires_at": expiration_time.isoformat()
        }
        
    except NotFound:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        print(f"Error retrieving file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {str(e)}")

@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file from both Cloud Storage and Firestore"""
    try:
        # Get file metadata from Firestore
        doc_ref = db.collection('uploaded_files').document(file_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_data = doc.to_dict()
        
        # Delete from Cloud Storage
        try:
            blob = bucket.blob(file_data['unique_name'])
            if blob.exists():
                blob.delete()
                print(f"Deleted file from Cloud Storage: {file_data['unique_name']}")
            else:
                print(f"File not found in Cloud Storage: {file_data['unique_name']}")
        except Exception as e:
            print(f"Error deleting from Cloud Storage: {e}")
            # Continue with Firestore deletion even if Cloud Storage deletion fails
        
        # Delete from uploaded_files collection
        doc_ref.delete()
        print(f"Deleted file metadata from Firestore: {file_id}")
        
        # Delete file messages from messages collection
        try:
            messages_query = db.collection('messages').where('type', '==', 'file').where('fileId', '==', file_id)
            messages = messages_query.stream()
            
            deleted_messages = 0
            for message_doc in messages:
                message_doc.reference.delete()
                deleted_messages += 1
                print(f"Deleted file message: {message_doc.id}")
            
            print(f"Deleted {deleted_messages} file messages")
            
        except Exception as e:
            print(f"Error deleting file messages: {e}")
            # Don't fail the entire operation if message deletion fails
        
        return {
            "success": True,
            "message": f"File '{file_data['original_name']}' deleted successfully",
            "file_id": file_id,
            "original_name": file_data['original_name']
        }
        
    except NotFound:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        print(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@app.delete("/messages/{message_id}")
async def delete_message(message_id: str):
    """Delete a message from Firestore"""
    try:
        # Get message from Firestore
        doc_ref = db.collection('messages').document(message_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Message not found")
        
        message_data = doc.to_dict()
        
        # If it's a file message, also delete the associated file
        if message_data.get('type') == 'file' and 'fileId' in message_data:
            try:
                # Delete the file as well
                file_doc_ref = db.collection('uploaded_files').document(message_data['fileId'])
                file_doc = file_doc_ref.get()
                
                if file_doc.exists:
                    file_data = file_doc.to_dict()
                    
                    # Delete from Cloud Storage
                    try:
                        blob = bucket.blob(file_data['unique_name'])
                        if blob.exists():
                            blob.delete()
                            print(f"Deleted file from Cloud Storage: {file_data['unique_name']}")
                    except Exception as e:
                        print(f"Error deleting from Cloud Storage: {e}")
                    
                    # Delete from uploaded_files
                    file_doc_ref.delete()
                    print(f"Deleted file metadata: {message_data['fileId']}")
                    
            except Exception as e:
                print(f"Error deleting associated file: {e}")
                # Continue with message deletion even if file deletion fails
        
        # Delete the message
        doc_ref.delete()
        print(f"Deleted message: {message_id}")
        
        return {
            "success": True,
            "message": "Message deleted successfully",
            "message_id": message_id
        }
        
    except NotFound:
        raise HTTPException(status_code=404, detail="Message not found")
    except Exception as e:
        print(f"Error deleting message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")

class BulkDeleteRequest(BaseModel):
    sender_name: Optional[str] = None
    filename_pattern: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    file_types: Optional[List[str]] = None

@app.post("/files/bulk-delete")
async def bulk_delete_files(request: BulkDeleteRequest):
    """Bulk delete files based on criteria"""
    try:
        deleted_files = 0
        deleted_messages = 0
        
        # Build query for uploaded_files
        files_query = db.collection('uploaded_files')
        
        # Apply filters
        if request.start_date and request.end_date:
            start_dt = datetime.fromisoformat(request.start_date)
            end_dt = datetime.fromisoformat(request.end_date)
            files_query = files_query.where('upload_time', '>=', start_dt).where('upload_time', '<=', end_dt)
        
        if request.filename_pattern:
            # Note: Firestore doesn't support regex, so we'll filter after fetching
            pass
        
        if request.file_types:
            files_query = files_query.where('content_type', 'in', request.file_types)
        
        # Execute query
        files_docs = files_query.stream()
        
        for file_doc in files_docs:
            file_data = file_doc.to_dict()
            
            # Apply filename pattern filter if specified
            if request.filename_pattern and request.filename_pattern.lower() not in file_data['original_name'].lower():
                continue
            
            print(f"Deleting file: {file_data['original_name']}")
            
            # Delete from Cloud Storage
            try:
                blob = bucket.blob(file_data['unique_name'])
                if blob.exists():
                    blob.delete()
                    print(f"  ✅ Deleted from Cloud Storage: {file_data['unique_name']}")
            except Exception as e:
                print(f"  ⚠️  Error deleting from Cloud Storage: {e}")
            
            # Delete from uploaded_files
            file_doc.reference.delete()
            deleted_files += 1
            print(f"  ✅ Deleted from uploaded_files: {file_doc.id}")
        
        # Delete file messages
        messages_query = db.collection('messages').where('type', '==', 'file')
        
        if request.sender_name:
            messages_query = messages_query.where('sender', '==', request.sender_name)
        
        if request.start_date and request.end_date:
            start_dt = datetime.fromisoformat(request.start_date)
            end_dt = datetime.fromisoformat(request.end_date)
            messages_query = messages_query.where('timestamp', '>=', start_dt).where('timestamp', '<=', end_dt)
        
        messages_docs = messages_query.stream()
        
        for message_doc in messages_docs:
            message_data = message_doc.to_dict()
            
            # Apply filename pattern filter if specified
            if request.filename_pattern and request.filename_pattern.lower() not in message_data.get('fileName', '').lower():
                continue
            
            print(f"Deleting file message: {message_doc.id}")
            message_doc.reference.delete()
            deleted_messages += 1
            print(f"  ✅ Deleted file message: {message_doc.id}")
        
        return {
            "success": True,
            "message": f"Bulk delete completed successfully",
            "deleted_files": deleted_files,
            "deleted_messages": deleted_messages,
            "total_deleted": deleted_files + deleted_messages
        }
        
    except Exception as e:
        print(f"Error in bulk delete: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to bulk delete files: {str(e)}")

# Socket.IO Event Handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    print(f"Client {sid} connected")
    await sio.emit('message', f"Client {sid} joined the whiteboard", room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f"Client {sid} disconnected")
    # Trigger user_left event when client disconnects
    await user_left(sid)

@sio.event
async def drawing(sid, data):
    """Handle drawing events and broadcast to all other clients"""
    print(f"Drawing event from {sid}: {data}")
    # Broadcast the drawing data to all other clients (excluding sender)
    await sio.emit('drawing', data, skip_sid=sid)

@sio.event
async def draw(sid, data):
    """Handle individual draw events and broadcast to all other clients"""
    print(f"Draw event from {sid}: {data}")
    # Broadcast the draw data to all other clients (excluding sender)
    await sio.emit('draw', data, skip_sid=sid)

@sio.event
async def clear(sid):
    """Handle clear events and broadcast to all other clients"""
    print(f"Clear event from {sid}")
    # Broadcast the clear event to all other clients (excluding sender)
    await sio.emit('clear', skip_sid=sid)

# Chat event handlers
@sio.event
async def join_chat(sid, data):
    """Handle user joining chat"""
    user_id = data.get('userId')
    user_name = data.get('userName')
    print(f"User {user_name} ({user_id}) joined chat")
    
    # Store user info in session
    await sio.save_session(sid, {'user_id': user_id, 'user_name': user_name})
    
    # Save user join event to Firestore
    try:
        user_event = {
            'type': 'user_joined',
            'user_id': user_id,
            'user_name': user_name,
            'timestamp': datetime.utcnow(),
            'session_id': sid
        }
        db.collection('chat_events').add(user_event)
    except Exception as e:
        print(f"Error saving user join event to Firestore: {e}")
    
    # Send recent messages to the newly joined user
    try:
        recent_messages = db.collection('messages').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(50).stream()
        messages_list = []
        for doc in recent_messages:
            msg_data = doc.to_dict()
            # Convert Firestore timestamp to milliseconds for frontend
            if 'timestamp' in msg_data:
                msg_data['timestamp'] = int(msg_data['timestamp'].timestamp() * 1000)
            messages_list.append(msg_data)
        
        # Send recent messages to the new user
        await sio.emit('recent_messages', list(reversed(messages_list)), room=sid)
    except Exception as e:
        print(f"Error retrieving recent messages: {e}")
    
    # Broadcast user joined to all clients
    await sio.emit('user_joined', {
        'id': user_id,
        'name': user_name,
        'isOnline': True,
        'timestamp': datetime.utcnow().isoformat()
    })

@sio.event
async def chat_message(sid, message_data):
    """Handle chat messages and save to Firestore"""
    session = await sio.get_session(sid)
    user_name = session.get('user_name', 'Unknown')
    user_id = session.get('user_id', 'unknown')
    
    # Prepare message for Firestore
    message_doc = {
        'id': message_data['id'],
        'type': message_data.get('type', 'text'),
        'content': message_data['content'],
        'sender': user_name,
        'sender_id': user_id,
        'timestamp': datetime.utcnow(),
        'session_id': sid
    }
    
    # Add file-specific fields if it's a file message
    if message_data.get('type') == 'file':
        message_doc.update({
            'fileName': message_data.get('fileName'),
            'fileSize': message_data.get('fileSize'),
            'fileType': message_data.get('fileType'),
            'downloadUrl': message_data.get('downloadUrl'),
            'fileId': message_data.get('fileId')
        })
    
    # Save message to Firestore
    try:
        db.collection('messages').add(message_doc)
        print(f"Message saved to Firestore from {user_name}: {message_data['content'][:50]}...")
    except Exception as e:
        print(f"Error saving message to Firestore: {e}")
    
    # Prepare message for broadcasting (use the original message_data structure)
    broadcast_message = {
        'id': message_data['id'],
        'type': message_data.get('type', 'text'),
        'content': message_data['content'],
        'sender': user_name,
        'timestamp': message_data['timestamp']
    }
    
    # Add file-specific fields for broadcast
    if message_data.get('type') == 'file':
        broadcast_message.update({
            'fileName': message_data.get('fileName'),
            'fileSize': message_data.get('fileSize'),
            'fileType': message_data.get('fileType'),
            'downloadUrl': message_data.get('downloadUrl'),
            'fileId': message_data.get('fileId')
        })
    
    # Broadcast message to all connected clients
    await sio.emit('chat_message', broadcast_message)

@sio.event
async def user_left(sid):
    """Handle user leaving chat"""
    session = await sio.get_session(sid)
    user_name = session.get('user_name', 'Unknown')
    user_id = session.get('user_id', 'unknown')
    
    print(f"User {user_name} ({user_id}) left chat")
    
    # Save user leave event to Firestore
    try:
        user_event = {
            'type': 'user_left',
            'user_id': user_id,
            'user_name': user_name,
            'timestamp': datetime.utcnow(),
            'session_id': sid
        }
        db.collection('chat_events').add(user_event)
    except Exception as e:
        print(f"Error saving user leave event to Firestore: {e}")
    
    # Broadcast user left to all clients
    await sio.emit('user_left', {
        'id': user_id,
        'name': user_name,
        'timestamp': datetime.utcnow().isoformat()
    })

# Create the ASGI application with Socket.IO
socket_app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host=HOST, port=PORT)
