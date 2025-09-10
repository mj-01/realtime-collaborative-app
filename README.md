# Real-time Collaborative Application

A full-stack real-time collaborative application built with Next.js, FastAPI, Socket.IO, and Google Cloud services.

## Features

- **Real-time Chat**: Live messaging with Socket.IO
- **Collaborative Whiteboard**: Multi-user drawing canvas
- **File Sharing**: Upload and preview files in chat
- **Data Persistence**: Messages and files saved to Firestore
- **User Presence**: See who's online and join/leave notifications
- **File Cleanup**: Tools for managing and deleting personal files

## Tech Stack

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.13, Socket.IO
- **Database**: Google Cloud Firestore
- **Storage**: Google Cloud Storage
- **Deployment**: Google Cloud Run

## Environment Configuration

This application uses environment variables for configuration. Copy the example files and update the values:

### Backend Environment Variables
```bash
cp .env.example backend/.env
```

### Frontend Environment Variables
```bash
cp frontend/.env.example frontend/.env.local
```

### Key Environment Variables

#### Backend (.env)
- `GOOGLE_SERVICE_ACCOUNT_KEY` - Google Cloud service account JSON
- `GCS_BUCKET_NAME` - Google Cloud Storage bucket name
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `MAX_FILE_SIZE_MB` - Maximum file upload size
- `ENABLE_FILE_UPLOAD` - Enable/disable file upload feature

#### Frontend (.env.local)
- `NEXT_PUBLIC_BACKEND_URL` - Backend API URL
- `NEXT_PUBLIC_FRONTEND_URL` - Frontend URL for display
- `NODE_ENV` - Environment (development/production)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/mj-01/realtime-collaborative-app.git
   cd realtime-collaborative-app
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cp .env.example backend/.env
   # Edit backend/.env with your values
   
   # Frontend
   cp frontend/.env.example frontend/.env.local
   # Edit frontend/.env.local with your values
   ```

3. **Install dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

4. **Run development servers**
   ```bash
   # Backend (Terminal 1)
   cd backend
   python main.py
   
   # Frontend (Terminal 2)
   cd frontend
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

## File Cleanup

The application includes tools for managing personal files:

- **Web Interface**: Hover over messages to see delete buttons
- **Cleanup Script**: `python cleanup_personal_files.py --interactive`
- **API Endpoints**: DELETE endpoints for files and messages

See [PERSONAL_FILE_CLEANUP_GUIDE.md](PERSONAL_FILE_CLEANUP_GUIDE.md) for detailed instructions.

## Deployment

### Google Cloud Run
- [Backend Deployment](backend/DEPLOYMENT.md)
- [Frontend Deployment](FRONTEND_DEPLOYMENT.md)

### Environment Variables in Production
Set these in your Cloud Run service:
- `GOOGLE_SERVICE_ACCOUNT_KEY`
- `GCS_BUCKET_NAME`
- `CORS_ORIGINS`
- `NEXT_PUBLIC_BACKEND_URL`
- `NEXT_PUBLIC_FRONTEND_URL`

## API Endpoints

### Backend API
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /upload` - File upload
- `GET /files/{file_id}` - Get file info
- `DELETE /files/{file_id}` - Delete file
- `DELETE /messages/{message_id}` - Delete message
- `POST /files/bulk-delete` - Bulk delete files

### Socket.IO Events
- `connect` - Client connection
- `disconnect` - Client disconnection
- `drawing` - Whiteboard drawing events
- `clear` - Clear whiteboard
- `chat_message` - Chat messages
- `join_chat` - User join notifications
- `user_left` - User leave notifications

## Development

### Project Structure
```
├── backend/           # FastAPI backend
├── frontend/          # Next.js frontend
├── benchmarks/        # ML benchmarking tools
├── tests/            # Test suite
├── .env.example      # Environment variables template
└── README.md         # This file
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT
