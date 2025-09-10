# 🔧 Environment Configuration Guide

This document explains all environment variables used in the application and how to configure them.

## 📁 Environment Files

- **Backend**: `backend/.env` (copy from `backend/.env.example`)
- **Frontend**: `frontend/.env.local` (copy from `frontend/.env.example`)

## 🔧 Backend Environment Variables

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8080` | Server port number |
| `DEBUG` | `false` | Enable debug mode (true/false) |

### Google Cloud Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_SERVICE_ACCOUNT_KEY` | `""` | Google Cloud service account JSON key |
| `GCS_BUCKET_NAME` | `labs-realtime-app-files` | Google Cloud Storage bucket name |
| `GOOGLE_CLOUD_PROJECT` | `""` | Google Cloud project ID |

### CORS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:3000,https://frontend-987275518911.us-central1.run.app` | Comma-separated list of allowed origins |

### File Upload Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_FILE_SIZE_MB` | `10` | Maximum file upload size in MB |
| `ALLOWED_FILE_TYPES` | `image/*,application/pdf,text/*,application/json` | Comma-separated list of allowed MIME types |

### Feature Flags

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_FILE_UPLOAD` | `true` | Enable/disable file upload feature |
| `ENABLE_REAL_TIME_CHAT` | `true` | Enable/disable real-time chat |
| `ENABLE_WHITEBOARD` | `true` | Enable/disable whiteboard feature |
| `ENABLE_FILE_CLEANUP` | `true` | Enable/disable file cleanup features |

### Security Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | `your-super-secret-jwt-key-here` | JWT secret key for authentication |
| `RATE_LIMIT_PER_MINUTE` | `60` | Rate limit for requests per minute |

### Logging Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## 🎨 Frontend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_BACKEND_URL` | `http://localhost:8000` | Backend API URL |
| `NEXT_PUBLIC_FRONTEND_URL` | `http://localhost:3000` | Frontend URL for display |
| `NODE_ENV` | `development` | Environment (development/production) |

## 🚀 Configuration Examples

### Development Environment

```bash
# backend/.env
HOST=0.0.0.0
PORT=8080
DEBUG=true
GOOGLE_SERVICE_ACCOUNT_KEY={"type":"service_account",...}
GCS_BUCKET_NAME=dev-realtime-app-files
GOOGLE_CLOUD_PROJECT=my-dev-project
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
MAX_FILE_SIZE_MB=5
ALLOWED_FILE_TYPES=image/*,text/*
ENABLE_FILE_UPLOAD=true
ENABLE_REAL_TIME_CHAT=true
ENABLE_WHITEBOARD=true
ENABLE_FILE_CLEANUP=true
JWT_SECRET=dev-secret-key
RATE_LIMIT_PER_MINUTE=120
LOG_LEVEL=DEBUG
```

```bash
# frontend/.env.local
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
NODE_ENV=development
```

### Production Environment

```bash
# backend/.env
HOST=0.0.0.0
PORT=8080
DEBUG=false
GOOGLE_SERVICE_ACCOUNT_KEY={"type":"service_account",...}
GCS_BUCKET_NAME=prod-realtime-app-files
GOOGLE_CLOUD_PROJECT=my-prod-project
CORS_ORIGINS=https://myapp.com,https://www.myapp.com
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=image/*,application/pdf,text/*,application/json
ENABLE_FILE_UPLOAD=true
ENABLE_REAL_TIME_CHAT=true
ENABLE_WHITEBOARD=true
ENABLE_FILE_CLEANUP=true
JWT_SECRET=super-secure-production-key
RATE_LIMIT_PER_MINUTE=60
LOG_LEVEL=INFO
```

```bash
# frontend/.env.local
NEXT_PUBLIC_BACKEND_URL=https://backend-123456789.us-central1.run.app
NEXT_PUBLIC_FRONTEND_URL=https://frontend-123456789.us-central1.run.app
NODE_ENV=production
```

## 🔒 Security Best Practices

### Environment Variable Security

1. **Never commit `.env` files** to version control
2. **Use strong secrets** for production environments
3. **Rotate secrets regularly** for security
4. **Use different secrets** for different environments
5. **Limit CORS origins** to only necessary domains

### Google Cloud Security

1. **Use least privilege** for service account permissions
2. **Rotate service account keys** regularly
3. **Use IAM roles** instead of service account keys when possible
4. **Enable audit logging** for security monitoring

## 🐛 Troubleshooting

### Common Issues

1. **CORS errors**: Check `CORS_ORIGINS` includes your frontend URL
2. **File upload fails**: Verify `MAX_FILE_SIZE_MB` and `ALLOWED_FILE_TYPES`
3. **Google Cloud errors**: Ensure `GOOGLE_SERVICE_ACCOUNT_KEY` is valid JSON
4. **Port conflicts**: Change `PORT` if 8080 is already in use

### Debug Mode

Enable debug mode to see detailed logs:

```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

### Validation

The application validates environment variables on startup. Check logs for any validation errors:

```bash
# Backend logs
python -m app.main

# Frontend logs
npm run dev
```

## 📝 Notes

- All boolean values should be `true` or `false` (case-insensitive)
- Comma-separated lists should not have spaces around commas
- File sizes are in MB for `MAX_FILE_SIZE_MB`
- Rate limits are per minute for `RATE_LIMIT_PER_MINUTE`
- Log levels are: `DEBUG`, `INFO`, `WARNING`, `ERROR`
