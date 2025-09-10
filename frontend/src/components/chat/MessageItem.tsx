/**
 * Individual message component.
 */

import React from 'react';
import { Message } from '../../types';
import { formatTime, isImage, isPDF } from '../../utils/formatters';

interface MessageItemProps {
  message: Message;
  currentUser: string | null;
  onDelete: (message: Message) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({
  message,
  currentUser,
  onDelete,
}) => {
  const isCurrentUser = message.sender === currentUser;
  const isSystemMessage = message.type === 'system';

  const handleDelete = () => {
    if (isCurrentUser && !isSystemMessage) {
      onDelete(message);
    }
  };

  const renderFileContent = () => {
    if (message.type !== 'file' || !message.fileName) return null;

    if (message.fileType && isImage(message.fileType)) {
      return (
        <div className="space-y-2">
          <img
            src={message.downloadUrl || message.content}
            alt={message.fileName}
            className="max-w-full max-h-64 rounded-lg object-contain"
            onError={(e) => {
              e.currentTarget.style.display = 'none';
              e.currentTarget.nextElementSibling?.classList.remove('hidden');
            }}
          />
          <div className="hidden flex items-center gap-2 p-2 bg-white bg-opacity-20 rounded">
            <div className="text-2xl">🖼️</div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{message.fileName}</div>
              <div className="text-xs opacity-75">
                {message.fileSize && formatFileSize(message.fileSize)}
              </div>
            </div>
          </div>
        </div>
      );
    }

    if (message.fileType && isPDF(message.fileType)) {
      return (
        <div className="space-y-2">
          <iframe
            src={message.downloadUrl || message.content}
            className="w-full h-64 rounded-lg border"
            title={message.fileName}
            onError={(e) => {
              e.currentTarget.style.display = 'none';
              e.currentTarget.nextElementSibling?.classList.remove('hidden');
            }}
          />
          <div className="hidden flex items-center gap-2 p-2 bg-white bg-opacity-20 rounded">
            <div className="text-2xl">📄</div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{message.fileName}</div>
              <div className="text-xs opacity-75">
                {message.fileSize && formatFileSize(message.fileSize)}
              </div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="flex items-center gap-2 p-2 bg-white bg-opacity-20 rounded">
        <div className="text-2xl">📎</div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate">{message.fileName}</div>
          <div className="text-xs opacity-75">
            {message.fileSize && formatFileSize(message.fileSize)}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg relative group ${
          isSystemMessage
            ? 'bg-yellow-100 text-yellow-800 text-center mx-auto'
            : isCurrentUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 text-gray-800'
        }`}
      >
        {isSystemMessage ? (
          <div className="text-sm font-medium">{message.content}</div>
        ) : message.type === 'file' ? (
          <div>
            <div className="font-medium text-sm mb-1">
              {!isCurrentUser && `${message.sender}:`}
            </div>
            {renderFileContent()}
          </div>
        ) : (
          <div>
            {!isCurrentUser && (
              <div className="text-xs font-medium mb-1">{message.sender}</div>
            )}
            <div className="text-sm">{message.content}</div>
          </div>
        )}
        
        <div className="text-xs opacity-75 mt-1">
          {formatTime(message.timestamp)}
        </div>
        
        {/* Delete button - only show for current user's messages and not system messages */}
        {isCurrentUser && !isSystemMessage && (
          <button
            onClick={handleDelete}
            className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1 rounded-full hover:bg-red-500 hover:bg-opacity-20"
            title="Delete message"
          >
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clipRule="evenodd" />
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

// Helper function for file size formatting
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};
