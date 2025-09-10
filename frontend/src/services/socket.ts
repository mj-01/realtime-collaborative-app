/**
 * Socket.IO service for real-time communication.
 */

import { io, Socket } from 'socket.io-client';
import { BACKEND_URL, SOCKET_EVENTS } from '../utils/constants';
import { Message, User } from '../types';

export class SocketService {
  private socket: Socket | null = null;

  connect(): Socket {
    if (this.socket?.connected) {
      return this.socket;
    }

    this.socket = io(BACKEND_URL, {
      transports: ['websocket', 'polling']
    });

    return this.socket;
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  joinChat(userId: string, userName: string): void {
    if (this.socket) {
      this.socket.emit(SOCKET_EVENTS.JOIN_CHAT, { userId, userName });
    }
  }

  sendMessage(message: Message): void {
    if (this.socket) {
      this.socket.emit(SOCKET_EVENTS.CHAT_MESSAGE, message);
    }
  }

  onMessage(callback: (message: Message) => void): void {
    if (this.socket) {
      this.socket.on(SOCKET_EVENTS.CHAT_MESSAGE, callback);
    }
  }

  onUserJoined(callback: (user: User) => void): void {
    if (this.socket) {
      this.socket.on(SOCKET_EVENTS.USER_JOINED, callback);
    }
  }

  onUserLeft(callback: (user: User) => void): void {
    if (this.socket) {
      this.socket.on(SOCKET_EVENTS.USER_LEFT, callback);
    }
  }

  onRecentMessages(callback: (messages: Message[]) => void): void {
    if (this.socket) {
      this.socket.on(SOCKET_EVENTS.RECENT_MESSAGES, callback);
    }
  }

  onConnect(callback: () => void): void {
    if (this.socket) {
      this.socket.on(SOCKET_EVENTS.CONNECT, callback);
    }
  }

  onDisconnect(callback: () => void): void {
    if (this.socket) {
      this.socket.on(SOCKET_EVENTS.DISCONNECT, callback);
    }
  }

  onError(callback: (error: Error) => void): void {
    if (this.socket) {
      this.socket.on('error', callback);
    }
  }

  getSocket(): Socket | null {
    return this.socket;
  }
}

// Export singleton instance
export const socketService = new SocketService();
