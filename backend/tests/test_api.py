"""
API endpoint tests for the backend.
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app

client = TestClient(app)

class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to the Backend API"}
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

class TestFileEndpoints:
    """Test file-related endpoints."""
    
    @patch('app.services.file_service.FileService.upload_file')
    @patch('app.services.firestore_service.FirestoreService.save_file_metadata')
    def test_upload_file_success(self, mock_save_metadata, mock_upload):
        """Test successful file upload."""
        # Mock the services
        from app.models.file import FileUploadResponse
        mock_upload.return_value = FileUploadResponse(
            success=True,
            file_id="test-file-id",
            original_name="test.txt",
            content_type="text/plain",
            size=10,
            download_url="https://example.com/test.txt",
            expires_at="2024-01-01T00:00:00"
        )
        mock_save_metadata.return_value = "test-file-id"
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                response = client.post("/files/upload", files={"file": f})
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["original_name"] == "test.txt"
        finally:
            os.unlink(temp_file_path)
    
    def test_upload_file_no_file(self):
        """Test file upload without file."""
        response = client.post("/files/upload")
        assert response.status_code == 422  # Validation error
    
    def test_upload_file_too_large(self):
        """Test file upload with file too large."""
        # Create a large file (simulate)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            f.write(large_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                response = client.post("/files/upload", files={"file": f})
            
            assert response.status_code == 400
            assert "File size exceeds" in response.json()["detail"]
        finally:
            os.unlink(temp_file_path)
    
    @patch('app.services.firestore_service.FirestoreService.get_file_metadata')
    @patch('app.services.file_service.FileService.get_file_info')
    def test_get_file_info_success(self, mock_get_info, mock_get_metadata):
        """Test successful file info retrieval."""
        mock_get_metadata.return_value = {
            "original_name": "test.txt",
            "unique_name": "unique-test.txt",
            "content_type": "text/plain",
            "size": 10,
            "upload_time": "2024-01-01T00:00:00",
            "public_url": "https://example.com/test.txt",
            "bucket_name": "test-bucket"
        }
        from app.models.file import FileInfo
        mock_get_info.return_value = FileInfo(
            file_id="test-file-id",
            original_name="test.txt",
            content_type="text/plain",
            size=10,
            upload_time="2024-01-01T00:00:00",
            download_url="https://example.com/test.txt",
            expires_at="2024-01-01T00:00:00"
        )
        
        response = client.get("/files/test-file-id")
        assert response.status_code == 200
        data = response.json()
        assert data["original_name"] == "test.txt"
    
    def test_get_file_info_not_found(self):
        """Test file info retrieval for non-existent file."""
        with patch('app.services.firestore_service.FirestoreService.get_file_metadata', return_value=None):
            response = client.get("/files/non-existent-id")
            assert response.status_code == 404
            assert response.json()["detail"] == "File not found"
    
    @patch('app.services.firestore_service.FirestoreService.get_file_metadata')
    @patch('app.services.file_service.FileService.delete_file')
    @patch('app.services.firestore_service.FirestoreService.delete_file_metadata')
    @patch('app.services.firestore_service.FirestoreService.delete_file_messages')
    def test_delete_file_success(self, mock_delete_messages, mock_delete_metadata, mock_delete_file, mock_get_metadata):
        """Test successful file deletion."""
        mock_get_metadata.return_value = {
            "original_name": "test.txt",
            "unique_name": "unique-test.txt"
        }
        mock_delete_file.return_value = True
        mock_delete_metadata.return_value = True
        mock_delete_messages.return_value = 2
        
        response = client.delete("/files/test-file-id")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["original_name"] == "test.txt"
    
    def test_delete_file_not_found(self):
        """Test file deletion for non-existent file."""
        with patch('app.services.firestore_service.FirestoreService.get_file_metadata', return_value=None):
            response = client.delete("/files/non-existent-id")
            assert response.status_code == 404
            assert response.json()["detail"] == "File not found"

class TestMessageEndpoints:
    """Test message-related endpoints."""
    
    @patch('app.services.firestore_service.FirestoreService.get_file_metadata')
    @patch('app.services.file_service.FileService.delete_file')
    @patch('app.services.firestore_service.FirestoreService.delete_message')
    def test_delete_message_success(self, mock_delete_message, mock_delete_file, mock_get_metadata):
        """Test successful message deletion."""
        mock_get_metadata.return_value = {
            "type": "text",
            "content": "test message"
        }
        mock_delete_message.return_value = True
        
        response = client.delete("/messages/test-message-id")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Message deleted successfully"
    
    def test_delete_message_not_found(self):
        """Test message deletion for non-existent message."""
        with patch('app.services.firestore_service.FirestoreService.get_file_metadata', return_value=None):
            response = client.delete("/messages/non-existent-id")
            assert response.status_code == 404
            assert response.json()["detail"] == "Message not found"

class TestBulkDeleteEndpoint:
    """Test bulk delete endpoint."""
    
    @patch('app.services.firestore_service.FirestoreService.bulk_delete_files')
    def test_bulk_delete_success(self, mock_bulk_delete):
        """Test successful bulk delete."""
        mock_bulk_delete.return_value = {
            "deleted_files": 5,
            "deleted_messages": 10,
            "total_deleted": 15
        }
        
        request_data = {
            "sender_name": "test_user",
            "filename_pattern": "test"
        }
        
        response = client.post("/files/bulk-delete", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted_files"] == 5
        assert data["deleted_messages"] == 10
        assert data["total_deleted"] == 15
