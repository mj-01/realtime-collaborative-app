'use client';

import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export default function DebugPage() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [messages, setMessages] = useState<string[]>([]);

  useEffect(() => {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    console.log('Debug: Connecting to backend URL:', backendUrl);
    
    const newSocket = io(backendUrl, {
      transports: ['websocket', 'polling']
    });

    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Debug: Connected to server');
      setConnectionStatus('Connected');
      setMessages(prev => [...prev, 'Connected to server']);
    });

    newSocket.on('disconnect', () => {
      console.log('Debug: Disconnected from server');
      setConnectionStatus('Disconnected');
      setMessages(prev => [...prev, 'Disconnected from server']);
    });

    newSocket.on('connect_error', (error) => {
      console.error('Debug: Connection error:', error);
      setConnectionStatus(`Error: ${error.message}`);
      setMessages(prev => [...prev, `Connection error: ${error.message}`]);
    });

    newSocket.on('error', (error) => {
      console.error('Debug: Socket error:', error);
      setMessages(prev => [...prev, `Socket error: ${error}`]);
    });

    return () => {
      newSocket.close();
    };
  }, []);

  const testMessage = () => {
    if (socket) {
      socket.emit('join_chat', { userId: 'test_user', userName: 'Test User' });
      setMessages(prev => [...prev, 'Sent join_chat event']);
    }
  };

  const testDrawing = () => {
    if (socket) {
      socket.emit('drawing', { type: 'start', strokeId: 'test', point: { x: 10, y: 10 }, color: '#000000', width: 2 });
      setMessages(prev => [...prev, 'Sent drawing event']);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Debug Page</h1>
      
      <div className="mb-4">
        <p className="text-lg">Connection Status: <span className={`font-bold ${connectionStatus === 'Connected' ? 'text-green-600' : 'text-red-600'}`}>{connectionStatus}</span></p>
      </div>

      <div className="mb-4">
        <button 
          onClick={testMessage}
          className="bg-blue-500 text-white px-4 py-2 rounded mr-2"
          disabled={!socket}
        >
          Test Chat Message
        </button>
        <button 
          onClick={testDrawing}
          className="bg-green-500 text-white px-4 py-2 rounded"
          disabled={!socket}
        >
          Test Drawing
        </button>
      </div>

      <div className="bg-gray-100 p-4 rounded">
        <h2 className="text-lg font-semibold mb-2">Messages:</h2>
        <div className="space-y-1">
          {messages.map((msg, index) => (
            <div key={index} className="text-sm">{msg}</div>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <h2 className="text-lg font-semibold mb-2">Environment Info:</h2>
        <div className="bg-gray-100 p-4 rounded">
          <p>Backend URL: {process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}</p>
          <p>Frontend URL: {process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000'}</p>
          <p>User Agent: {typeof window !== 'undefined' ? window.navigator.userAgent : 'Server-side'}</p>
        </div>
      </div>
    </div>
  );
}
