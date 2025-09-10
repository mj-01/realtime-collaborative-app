"""
Main FastAPI application with modular structure.
"""
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_socketio import SocketManager

from app.config import settings
from app.routes import files, messages, health, metrics
from app.middleware.metrics import MetricsMiddleware
from app.utils.logging import get_logger

# Initialize logger
logger = get_logger("main")

# Create FastAPI app
app = FastAPI(
    title="Backend API", 
    version="1.0.0",
    description="Real-time collaborative application backend"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware
metrics_middleware = MetricsMiddleware(app)
app.add_middleware(MetricsMiddleware)

# Initialize Socket.IO
sio = socketio.AsyncServer(
    cors_allowed_origins=settings.cors_origins,
    async_mode='asgi'
)
socket_manager = SocketManager(app=app, socketio_server=sio)

# Include routers
app.include_router(health.router)
app.include_router(files.router)
app.include_router(messages.router)
app.include_router(metrics.router)

# Set global metrics middleware for dependency injection
metrics.metrics_middleware = metrics_middleware

# Socket.IO Event Handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    logger.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {sid}")

@sio.event
async def join_chat(sid, data):
    """Handle user joining chat."""
    user_id = data.get('userId')
    user_name = data.get('userName')
    logger.info(f"User {user_name} ({user_id}) joined chat")
    
    # Store user info in session
    await sio.save_session(sid, {'user_id': user_id, 'user_name': user_name})
    
    # Broadcast user joined to all clients
    await sio.emit('user_joined', {
        'id': user_id,
        'name': user_name,
        'isOnline': True,
    })

@sio.event
async def chat_message(sid, message_data):
    """Handle chat messages and save to Firestore."""
    session = await sio.get_session(sid)
    user_name = session.get('user_name', 'Unknown')
    user_id = session.get('user_id', 'unknown')
    
    logger.info(f"Message from {user_name}: {message_data['content'][:50]}...")
    
    # Broadcast message to all connected clients
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
    
    await sio.emit('chat_message', broadcast_message)

@sio.event
async def drawing(sid, data):
    """Handle whiteboard drawing events."""
    # Broadcast drawing events to all other clients
    await sio.emit('drawing', data, skip_sid=sid)

@sio.event
async def clear(sid):
    """Handle clear whiteboard events."""
    await sio.emit('clear', skip_sid=sid)

# Create the ASGI application with Socket.IO
socket_app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(socket_app, host=settings.host, port=settings.port)
