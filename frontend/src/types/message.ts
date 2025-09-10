/**
 * Message-related type definitions.
 */

export interface Message {
  id: string;
  type: 'text' | 'file' | 'system';
  content: string;
  sender: string;
  timestamp: number;
  fileName?: string;
  fileSize?: number;
  fileType?: string;
  downloadUrl?: string;
  fileId?: string;
}

export interface User {
  id: string;
  name: string;
  isOnline: boolean;
}

export interface FileUploadResult {
  success: boolean;
  file_id: string;
  original_name: string;
  content_type: string;
  size: number;
  download_url: string;
  expires_at: string;
}
