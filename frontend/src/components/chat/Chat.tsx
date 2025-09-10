/**
 * Main Chat component with modular structure.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Message, User } from '../../types';
import { useSocket } from '../../hooks/useSocket';
import { useFileUpload } from '../../hooks/useFileUpload';
import { deleteFile, deleteMessage } from '../../services/api';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { UserList } from './UserList';

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  
  const { socket, isConnected, joinChat, sendMessage } = useSocket();
  const { upload, isUploading } = useFileUpload();

  // Initialize socket connection and event handlers
  useEffect(() => {
    if (!socket) return;

    // Generate a random user name for demo
    const userId = `user_${Math.random().toString(36).substr(2, 9)}`;
    const userName = `User ${Math.floor(Math.random() * 1000)}`;
    const user = { id: userId, name: userName, isOnline: true };
    setCurrentUser(user);
    
    // Join chat
    joinChat(userId, userName);

    // Event handlers
    const handleMessage = (message: Message) => {
      setMessages(prev => [...prev, message]);
    };

    const handleUserJoined = (user: User) => {
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
    };

    const handleUserLeft = (user: User) => {
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
    };

    const handleUsersList = (usersList: User[]) => {
      setUsers(usersList);
    };

    const handleRecentMessages = (messagesList: Message[]) => {
      setMessages(messagesList);
    };

    // Register event listeners
    socket.on('chat_message', handleMessage);
    socket.on('user_joined', handleUserJoined);
    socket.on('user_left', handleUserLeft);
    socket.on('users_list', handleUsersList);
    socket.on('recent_messages', handleRecentMessages);

    return () => {
      socket.off('chat_message', handleMessage);
      socket.off('user_joined', handleUserJoined);
      socket.off('user_left', handleUserLeft);
      socket.off('users_list', handleUsersList);
      socket.off('recent_messages', handleRecentMessages);
    };
  }, [socket, joinChat]);

  // Send text message
  const handleSendMessage = useCallback((content: string) => {
    if (!currentUser) return;

    const message: Message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: 'text',
      content,
      sender: currentUser.name,
      timestamp: Date.now(),
    };

    sendMessage(message);
  }, [currentUser, sendMessage]);

  // Handle file upload
  const handleFileUpload = useCallback(async (file: File) => {
    if (!currentUser) return;

    try {
      const uploadResult = await upload(file);
      
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

      sendMessage(message);
    } catch (error) {
      console.error('File upload error:', error);
      alert('Failed to upload file. Please try again.');
    }
  }, [currentUser, upload, sendMessage]);

  // Delete file
  const handleDeleteFile = useCallback(async (message: Message) => {
    if (message.type !== 'file' || !message.fileId) return;
    
    if (!confirm(`Are you sure you want to delete "${message.fileName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await deleteFile(message.fileId);
      setMessages(prev => prev.filter(msg => msg.id !== message.id));
      console.log('File deleted successfully');
    } catch (error) {
      console.error('File delete error:', error);
      alert('Failed to delete file. Please try again.');
    }
  }, []);

  // Delete message
  const handleDeleteMessage = useCallback(async (message: Message) => {
    if (message.type === 'system') return;
    
    if (!confirm(`Are you sure you want to delete this message? This action cannot be undone.`)) {
      return;
    }

    try {
      if (message.type === 'file' && message.fileId) {
        await deleteFile(message.fileId);
      } else {
        await deleteMessage(message.id);
      }
      
      setMessages(prev => prev.filter(msg => msg.id !== message.id));
      console.log('Message deleted successfully');
    } catch (error) {
      console.error('Message delete error:', error);
      alert('Failed to delete message. Please try again.');
    }
  }, []);

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
        
        <UserList users={users} />
      </div>

      {/* Messages */}
      <MessageList
        messages={messages}
        currentUser={currentUser?.name || null}
        onDeleteMessage={handleDeleteMessage}
      />

      {/* Input */}
      <MessageInput
        onSendMessage={handleSendMessage}
        onFileUpload={handleFileUpload}
        disabled={!isConnected}
      />
    </div>
  );
};
