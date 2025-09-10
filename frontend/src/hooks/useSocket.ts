/**
 * Custom hook for Socket.IO connection management.
 */

import { useEffect, useState, useCallback } from 'react';
import { socketService } from '../services/socket';
import { Message, User } from '../types';

export const useSocket = () => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
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

    newSocket.on('connect', handleConnect);
    newSocket.on('disconnect', handleDisconnect);
    newSocket.on('error', handleError);

    return () => {
      newSocket.off('connect', handleConnect);
      newSocket.off('disconnect', handleDisconnect);
      newSocket.off('error', handleError);
      socketService.disconnect();
    };
  }, []);

  const joinChat = useCallback((userId: string, userName: string) => {
    socketService.joinChat(userId, userName);
  }, []);

  const sendMessage = useCallback((message: Message) => {
    socketService.sendMessage(message);
  }, []);

  return {
    socket,
    isConnected,
    joinChat,
    sendMessage,
  };
};
