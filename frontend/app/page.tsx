'use client';

import { useState } from 'react';
import Whiteboard from '../src/components/Whiteboard';
import Chat from '../src/components/Chat';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'whiteboard' | 'chat'>('whiteboard');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                🎨 Realtime Collaborative App
              </h1>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => setActiveTab('whiteboard')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'whiteboard'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                🎨 Whiteboard
              </button>
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'chat'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                💬 Chat
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'whiteboard' && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-4 border-b">
              <h2 className="text-lg font-semibold text-gray-900">
                Collaborative Whiteboard
              </h2>
              <p className="text-sm text-gray-600">
                Draw together in real-time with other users
              </p>
            </div>
            <div className="p-4">
              <Whiteboard />
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-4 border-b">
              <h2 className="text-lg font-semibold text-gray-900">
                Real-time Chat
              </h2>
              <p className="text-sm text-gray-600">
                Chat with other users and share files
              </p>
            </div>
            <div className="p-4">
              <Chat />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>
              Built with Next.js, FastAPI, Socket.IO, and Google Cloud
            </p>
            <p className="mt-2">
              Frontend: <a href={process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000'} className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">Cloud Run</a> | 
              Backend: <a href={process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'} className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">Cloud Run</a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
