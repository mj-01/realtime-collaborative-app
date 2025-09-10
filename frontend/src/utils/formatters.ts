/**
 * Utility functions for formatting data.
 */

/**
 * Format file size in bytes to human readable format.
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Format timestamp to time string.
 */
export const formatTime = (timestamp: number): string => {
  return new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

/**
 * Check if file is an image.
 */
export const isImage = (fileType: string): boolean => {
  return fileType.startsWith('image/');
};

/**
 * Check if file is a PDF.
 */
export const isPDF = (fileType: string): boolean => {
  return fileType === 'application/pdf';
};
