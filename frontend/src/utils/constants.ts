/**
 * Application constants.
 */

export const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export const SOCKET_EVENTS = {
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  JOIN_CHAT: 'join_chat',
  CHAT_MESSAGE: 'chat_message',
  USER_JOINED: 'user_joined',
  USER_LEFT: 'user_left',
  RECENT_MESSAGES: 'recent_messages',
  DRAWING: 'drawing',
  CLEAR: 'clear',
} as const;

export const MESSAGE_TYPES = {
  TEXT: 'text',
  FILE: 'file',
  SYSTEM: 'system',
} as const;
