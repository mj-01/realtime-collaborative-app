'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

interface Message {
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

interface User {
  id: string;
  name: string;
  isOnline: boolean;
}

const Chat: React.FC = () => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [users, setUsers] = useState<User[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Initialize socket connection
  useEffect(() => {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    console.log('Connecting to backend URL:', backendUrl);
    
    const newSocket = io(backendUrl, {
      transports: ['websocket', 'polling']
    });

    setSocket(newSocket);

    // Connection events
    newSocket.on('connect', () => {
      console.log('Connected to chat server');
      setIsConnected(true);
      
      // Generate a random user name for demo
      const userId = `user_${Math.random().toString(36).substr(2, 9)}`;
      const userName = `User ${Math.floor(Math.random() * 1000)}`;
      const user = { id: userId, name: userName, isOnline: true };
      setCurrentUser(user);
      
      // Join chat
      newSocket.emit('join_chat', { userId, userName });
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from chat server');
      setIsConnected(false);
    });

    newSocket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
    });

    newSocket.on('error', (error) => {
      console.error('Socket error:', error);
    });

    // Chat events
    newSocket.on('chat_message', (message: Message) => {
      setMessages(prev => [...prev, message]);
    });

    newSocket.on('user_joined', (user: User) => {
      setUsers(prev => {
        const exists = prev.find(u => u.id === user.id);
        if (exists) {
          return prev.map(u => u.id === user.id ? { ...u, isOnline: true } : u);
        }
        return [...prev, user];
      });
      
      // Add system message
      setMessages(prev => [...prev, {
        id: `system_${Date.now()}`,
        type: 'system',
        content: `${user.name} joined the chat`,
        sender: 'system',
        timestamp: Date.now()
      }]);
    });

    newSocket.on('user_left', (user: User) => {
      setUsers(prev => {
        const userExists = prev.find(u => u.id === user.id);
        if (userExists) {
          // Add system message
          setMessages(prev => [...prev, {
            id: `system_${Date.now()}`,
            type: 'system',
            content: `${user.name} left the chat`,
            sender: 'system',
            timestamp: Date.now()
          }]);
          
          return prev.map(u => u.id === user.id ? { ...u, isOnline: false } : u);
        }
        return prev;
      });
    });

    newSocket.on('users_list', (usersList: User[]) => {
      setUsers(usersList);
    });

    newSocket.on('recent_messages', (messagesList: Message[]) => {
      setMessages(messagesList);
    });

    return () => {
      newSocket.close();
    };
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send text message
  const sendMessage = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || !socket || !currentUser) return;

    const message: Message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: 'text',
      content: newMessage.trim(),
      sender: currentUser.name,
      timestamp: Date.now()
    };

    socket.emit('chat_message', message);
    setNewMessage('');
  }, [newMessage, socket, currentUser]);

  // Handle file upload
  const handleFileUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !socket || !currentUser) return;

    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      alert('File size must be less than 10MB');
      return;
    }

    setIsUploading(true);

    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);

      // Upload file to backend
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const uploadResult = await response.json();
      
      // Create message with file info
      const message: Message = {
        id: `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'file',
        content: uploadResult.download_url,
        sender: currentUser.name,
        timestamp: Date.now(),
        fileName: uploadResult.original_name,
        fileSize: uploadResult.size,
        fileType: uploadResult.content_type,
        downloadUrl: uploadResult.download_url,
        fileId: uploadResult.file_id
      };

      // Send message via socket
      socket.emit('chat_message', message);
      
    } catch (error) {
      console.error('File upload error:', error);
      alert('Failed to upload file. Please try again.');
    } finally {
      setIsUploading(false);
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }, [socket, currentUser]);

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Format timestamp
  const formatTime = (timestamp: number): string => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Download file
  const downloadFile = (message: Message) => {
    if (message.type !== 'file' || !message.fileName) return;
    
    const link = document.createElement('a');
    link.href = message.downloadUrl || message.content;
    link.download = message.fileName;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Delete file
  const deleteFile = async (message: Message) => {
    if (message.type !== 'file' || !message.fileId) return;
    
    if (!confirm(`Are you sure you want to delete "${message.fileName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/files/${message.fileId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Delete failed: ${response.statusText}`);
      }

      // Remove the message from the local state
      setMessages(prev => prev.filter(msg => msg.id !== message.id));
      
      console.log('File deleted successfully');
    } catch (error) {
      console.error('File delete error:', error);
      alert('Failed to delete file. Please try again.');
    }
  };

  // Delete message
  const deleteMessage = async (message: Message) => {
    if (message.type === 'system') return;
    
    if (!confirm(`Are you sure you want to delete this message? This action cannot be undone.`)) {
      return;
    }

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/messages/${message.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Delete failed: ${response.statusText}`);
      }

      // Remove the message from the local state
      setMessages(prev => prev.filter(msg => msg.id !== message.id));
      
      console.log('Message deleted successfully');
    } catch (error) {
      console.error('Message delete error:', error);
      alert('Failed to delete message. Please try again.');
    }
  };

  // Check if file is an image
  const isImage = (fileType: string): boolean => {
    return fileType.startsWith('image/');
  };

  // Check if file is a PDF
  const isPDF = (fileType: string): boolean => {
    return fileType === 'application/pdf';
  };

  return (
    <div className="flex flex-col h-full bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-gray-800">Chat</h3>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        
        {/* Online Users */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Online:</span>
          <div className="flex -space-x-2">
            {users.filter(user => user.isOnline).slice(0, 5).map((user, index) => (
              <div
                key={user.id}
                className="w-6 h-6 bg-blue-500 rounded-full border-2 border-white flex items-center justify-center text-xs text-white font-medium"
                title={user.name}
              >
                {user.name.charAt(0).toUpperCase()}
              </div>
            ))}
            {users.filter(user => user.isOnline).length > 5 && (
              <div className="w-6 h-6 bg-gray-400 rounded-full border-2 border-white flex items-center justify-center text-xs text-white font-medium">
                +{users.filter(user => user.isOnline).length - 5}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === currentUser?.name ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg relative group ${
                message.type === 'system'
                  ? 'bg-yellow-100 text-yellow-800 text-center mx-auto'
                  : message.sender === currentUser?.name
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {message.type === 'system' ? (
                <div className="text-sm font-medium">{message.content}</div>
              ) : message.type === 'file' ? (
                <div>
                  <div className="font-medium text-sm mb-1">
                    {message.sender !== currentUser?.name && `${message.sender}:`}
                  </div>
                  
                  {/* File preview or info */}
                  {message.fileType && isImage(message.fileType) ? (
                    <div className="space-y-2">
                      <img
                        src={message.downloadUrl || message.content}
                        alt={message.fileName}
                        className="max-w-full max-h-64 rounded-lg object-contain"
                        onError={(e) => {
                          // Fallback to file info if image fails to load
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
                        <button
                          onClick={() => downloadFile(message)}
                          className="text-xs px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded transition-colors"
                        >
                          Download
                        </button>
                      </div>
                    </div>
                  ) : message.fileType && isPDF(message.fileType) ? (
                    <div className="space-y-2">
                      <iframe
                        src={message.downloadUrl || message.content}
                        className="w-full h-64 rounded-lg border"
                        title={message.fileName}
                        onError={(e) => {
                          // Fallback to file info if PDF fails to load
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
                        <button
                          onClick={() => downloadFile(message)}
                          className="text-xs px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded transition-colors"
                        >
                          Download
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 p-2 bg-white bg-opacity-20 rounded">
                      <div className="text-2xl">📎</div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate">{message.fileName}</div>
                        <div className="text-xs opacity-75">
                          {message.fileSize && formatFileSize(message.fileSize)}
                        </div>
                      </div>
                      <button
                        onClick={() => downloadFile(message)}
                        className="text-xs px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded transition-colors"
                      >
                        Download
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div>
                  {message.sender !== currentUser?.name && (
                    <div className="text-xs font-medium mb-1">{message.sender}</div>
                  )}
                  <div className="text-sm">{message.content}</div>
                </div>
              )}
              <div className="text-xs opacity-75 mt-1">
                {formatTime(message.timestamp)}
              </div>
              
              {/* Delete button - only show for current user's messages and not system messages */}
              {message.sender === currentUser?.name && message.type !== 'system' && (
                <button
                  onClick={() => message.type === 'file' ? deleteFile(message) : deleteMessage(message)}
                  className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1 rounded-full hover:bg-red-500 hover:bg-opacity-20"
                  title={message.type === 'file' ? 'Delete file' : 'Delete message'}
                >
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clipRule="evenodd" />
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <form onSubmit={sendMessage} className="flex gap-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
            disabled={!isConnected}
          />
          
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileUpload}
            className="hidden"
            accept="*/*"
          />
          
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={!isConnected || isUploading}
            className="px-3 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title={isUploading ? "Uploading..." : "Upload file"}
          >
            {isUploading ? "⏳" : "📎"}
          </button>
          
          <button
            type="submit"
            disabled={!isConnected || !newMessage.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
