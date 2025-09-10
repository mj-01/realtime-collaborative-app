/**
 * Tests for API service.
 */

import { uploadFile, deleteFile, deleteMessage } from '../../services/api';

// Mock fetch
global.fetch = jest.fn();

describe('API Service', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  describe('uploadFile', () => {
    it('uploads file successfully', async () => {
      const mockResponse = {
        success: true,
        file_id: 'test-id',
        original_name: 'test.txt',
        content_type: 'text/plain',
        size: 10,
        download_url: 'https://example.com/test.txt',
        expires_at: '2024-01-01T00:00:00',
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const result = await uploadFile(file);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/upload'),
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('throws error on upload failure', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        statusText: 'Upload failed',
      });

      const file = new File(['test content'], 'test.txt', { type: 'text/plain' });

      await expect(uploadFile(file)).rejects.toThrow('Upload failed: Upload failed');
    });
  });

  describe('deleteFile', () => {
    it('deletes file successfully', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
      });

      await deleteFile('test-file-id');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/files/test-file-id'),
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });

    it('throws error on delete failure', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        statusText: 'Delete failed',
      });

      await expect(deleteFile('test-file-id')).rejects.toThrow('Delete failed: Delete failed');
    });
  });

  describe('deleteMessage', () => {
    it('deletes message successfully', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
      });

      await deleteMessage('test-message-id');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/messages/test-message-id'),
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });

    it('throws error on delete failure', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        statusText: 'Delete failed',
      });

      await expect(deleteMessage('test-message-id')).rejects.toThrow('Delete failed: Delete failed');
    });
  });
});
