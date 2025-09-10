/**
 * Custom hook for Socket.IO connection management.
 */

import { useEffect, useState, useCallback } from 'react';
import { Socket } from 'socket.io-client';
import { socketService } from '../services/socket';
import { Message, User } from '../types';

export const useSocket = () => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Get the socket from the service
    const newSocket = socketService.connect();
    setSocket(newSocket);

    const handleConnect = () => {
      console.log('Connected to chat server');
      setIsConnected(true);
    };

    const handleDisconnect = () => {
      console.log('Disconnected from chat server');
      setIsConnected(false);
    };

    const handleError = (error: Error) => {
      console.error('Socket error:', error);
    };

    // Add event listeners
    newSocket.on('connect', handleConnect);
    newSocket.on('disconnect', handleDisconnect);
    newSocket.on('error', handleError);

    // Check initial connection state
    setIsConnected(newSocket.connected);

    return () => {
      newSocket.off('connect', handleConnect);
      newSocket.off('disconnect', handleDisconnect);
      newSocket.off('error', handleError);
    };
  }, []);

  const joinChat = useCallback((userId: string, userName: string) => {
    if (socket) {
      socket.emit('join_chat', { userId, userName });
    }
  }, [socket]);

  const sendMessage = useCallback((message: Message) => {
    if (socket) {
      socket.emit('chat_message', message);
    }
  }, [socket]);

  return {
    socket,
    isConnected,
    joinChat,
    sendMessage,
  };
};
