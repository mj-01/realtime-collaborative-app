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
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8080)
- `DEBUG` - Debug mode (default: false)
- `GOOGLE_SERVICE_ACCOUNT_KEY` - Google Cloud service account JSON
- `GCS_BUCKET_NAME` - Google Cloud Storage bucket name
- `GOOGLE_CLOUD_PROJECT` - Google Cloud project ID
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `MAX_FILE_SIZE_MB` - Maximum file upload size (default: 10)
- `ALLOWED_FILE_TYPES` - Allowed file types (comma-separated)
- `ENABLE_FILE_UPLOAD` - Enable/disable file upload feature
- `ENABLE_REAL_TIME_CHAT` - Enable/disable real-time chat
- `ENABLE_WHITEBOARD` - Enable/disable whiteboard feature
- `ENABLE_FILE_CLEANUP` - Enable/disable file cleanup features
- `JWT_SECRET` - JWT secret key for authentication
- `RATE_LIMIT_PER_MINUTE` - Rate limit for requests (default: 60)
- `LOG_LEVEL` - Logging level (default: INFO)

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

## Testing

The application includes a comprehensive test suite with 100% passing tests.

### Running Tests

#### All Tests (Recommended)
```bash
# Run all backend and frontend tests
./run_tests.sh
```

#### Backend Tests Only
```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

#### Frontend Tests Only
```bash
cd frontend
npm test
```

### Test Coverage

| Test Category | Status | Coverage |
|---------------|--------|----------|
| **Backend API Tests** | ✅ Passing | 12/12 tests (100%) |
| **Frontend Component Tests** | ✅ Passing | 21/21 tests (100%) |
| **Overall Test Suite** | ✅ Passing | 33/33 tests (100%) |

### Test Types

#### Backend Tests
- **API Endpoint Tests**: All REST endpoints tested with mocked dependencies
- **Error Handling Tests**: Edge cases and error scenarios
- **Mocking**: Proper mocking of external dependencies (Firestore, GCS)

#### Frontend Tests
- **Component Tests**: React components tested with React Testing Library
- **Service Tests**: API service functions tested with mocked fetch
- **Hook Tests**: Custom hooks tested for proper behavior
- **User Interaction Tests**: Form submissions, button clicks, etc.

### Test Dependencies

#### Backend Test Dependencies
```bash
cd backend
pip install pytest pytest-asyncio httpx psutil
```

#### Frontend Test Dependencies
```bash
cd frontend
npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

### Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```bash
# Example CI script
./run_tests.sh
if [ $? -eq 0 ]; then
    echo "All tests passed!"
    exit 0
else
    echo "Tests failed!"
    exit 1
fi
```

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
├── backend/                    # FastAPI backend
│   ├── app/                   # Application modules
│   │   ├── config.py         # Configuration management
│   │   ├── models/           # Pydantic models
│   │   ├── routes/           # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── middleware/       # Custom middleware
│   │   └── utils/            # Utility functions
│   ├── tests/                # Backend tests
│   │   └── test_api.py       # API endpoint tests
│   ├── requirements.txt      # Python dependencies
│   └── main.py              # Application entry point
├── frontend/                  # Next.js frontend
│   ├── src/                  # Source code
│   │   ├── components/       # React components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API services
│   │   ├── types/           # TypeScript types
│   │   └── utils/           # Utility functions
│   ├── src/__tests__/       # Frontend tests
│   ├── package.json         # Node.js dependencies
│   └── jest.config.js       # Jest configuration
├── benchmarks/               # ML benchmarking tools
├── .env.example             # Environment variables template
├── run_tests.sh            # Test runner script
└── README.md               # This file
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. **Run the test suite**: `./run_tests.sh`
5. Ensure all tests pass (100% success rate)
6. Submit a pull request

**Note**: All pull requests must pass the complete test suite before merging.

## TODO / Future Improvements

The following features are planned for future releases but are currently out of scope:

### Security & Authentication
- **Authentication System** - All endpoints are currently public
- **File Access Control** - Files are made public immediately (security risk)
- **Rate Limiting** - No protection against abuse/DoS attacks
- **Enhanced File Validation** - Limited file type validation (potential security risk)

### Additional Features
- **User Management** - User registration, login, profiles
- **File Permissions** - Private files, sharing controls
- **Advanced Security** - CSRF protection, input sanitization
- **Monitoring & Alerts** - Error tracking, performance monitoring

*These items are documented for future development and do not affect current functionality.*

## License

MIT
