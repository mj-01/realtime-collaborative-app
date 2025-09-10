/**
 * API service for backend communication.
 */

import { BACKEND_URL } from '../utils/constants';
import { FileUploadResult } from '../types';

/**
 * Upload a file to the backend.
 */
export const uploadFile = async (file: File): Promise<FileUploadResult> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BACKEND_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Delete a file by ID.
 */
export const deleteFile = async (fileId: string): Promise<void> => {
  const response = await fetch(`${BACKEND_URL}/files/${fileId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error(`Delete failed: ${response.statusText}`);
  }
};

/**
 * Delete a message by ID.
 */
export const deleteMessage = async (messageId: string): Promise<void> => {
  const response = await fetch(`${BACKEND_URL}/messages/${messageId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error(`Delete failed: ${response.statusText}`);
  }
};
