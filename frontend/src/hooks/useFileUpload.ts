/**
 * Custom hook for file upload functionality.
 */

import { useState, useCallback } from 'react';
import { uploadFile, deleteFile } from '../services/api';
import { FileUploadResult } from '../types';

export const useFileUpload = () => {
  const [isUploading, setIsUploading] = useState(false);

  const upload = useCallback(async (file: File): Promise<FileUploadResult> => {
    setIsUploading(true);
    try {
      const result = await uploadFile(file);
      return result;
    } finally {
      setIsUploading(false);
    }
  }, []);

  const remove = useCallback(async (fileId: string): Promise<void> => {
    await deleteFile(fileId);
  }, []);

  return {
    isUploading,
    upload,
    remove,
  };
};
