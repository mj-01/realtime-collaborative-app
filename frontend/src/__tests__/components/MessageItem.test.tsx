/**
 * Tests for MessageItem component.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MessageItem } from '../../components/chat/MessageItem';
import { Message } from '../../types';

// Mock the formatters
jest.mock('../../utils/formatters', () => ({
  formatTime: (timestamp: number) => new Date(timestamp).toLocaleTimeString(),
  isImage: (fileType: string) => fileType.startsWith('image/'),
  isPDF: (fileType: string) => fileType === 'application/pdf',
}));

describe('MessageItem', () => {
  const mockOnDelete = jest.fn();
  const currentUser = 'testuser';

  const textMessage: Message = {
    id: '1',
    type: 'text',
    content: 'Hello world',
    sender: 'testuser',
    timestamp: Date.now(),
  };

  const fileMessage: Message = {
    id: '2',
    type: 'file',
    content: 'https://example.com/file.pdf',
    sender: 'testuser',
    timestamp: Date.now(),
    fileName: 'document.pdf',
    fileSize: 1024,
    fileType: 'application/pdf',
    downloadUrl: 'https://example.com/file.pdf',
    fileId: 'file123',
  };

  const systemMessage: Message = {
    id: '3',
    type: 'system',
    content: 'User joined the chat',
    sender: 'system',
    timestamp: Date.now(),
  };

  beforeEach(() => {
    mockOnDelete.mockClear();
  });

  it('renders text message correctly', () => {
    render(
      <MessageItem
        message={textMessage}
        currentUser={currentUser}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('Hello world')).toBeInTheDocument();
    // Current user's messages don't show sender name
    expect(screen.queryByText('testuser')).not.toBeInTheDocument();
  });

  it('renders file message correctly', () => {
    render(
      <MessageItem
        message={fileMessage}
        currentUser={currentUser}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('document.pdf')).toBeInTheDocument();
    expect(screen.getByText('1 KB')).toBeInTheDocument();
  });

  it('renders system message correctly', () => {
    render(
      <MessageItem
        message={systemMessage}
        currentUser={currentUser}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('User joined the chat')).toBeInTheDocument();
  });

  it('shows delete button for current user messages', () => {
    render(
      <MessageItem
        message={textMessage}
        currentUser={currentUser}
        onDelete={mockOnDelete}
      />
    );

    const deleteButton = screen.getByTitle('Delete message');
    expect(deleteButton).toBeInTheDocument();
  });

  it('does not show delete button for system messages', () => {
    render(
      <MessageItem
        message={systemMessage}
        currentUser={currentUser}
        onDelete={mockOnDelete}
      />
    );

    const deleteButton = screen.queryByTitle('Delete message');
    expect(deleteButton).not.toBeInTheDocument();
  });

  it('calls onDelete when delete button is clicked', () => {
    render(
      <MessageItem
        message={textMessage}
        currentUser={currentUser}
        onDelete={mockOnDelete}
      />
    );

    const deleteButton = screen.getByTitle('Delete message');
    fireEvent.click(deleteButton);

    expect(mockOnDelete).toHaveBeenCalledWith(textMessage);
  });

  it('does not show delete button for other users messages', () => {
    const otherUserMessage = { ...textMessage, sender: 'otheruser' };
    
    render(
      <MessageItem
        message={otherUserMessage}
        currentUser={currentUser}
        onDelete={mockOnDelete}
      />
    );

    const deleteButton = screen.queryByTitle('Delete message');
    expect(deleteButton).not.toBeInTheDocument();
  });

  it('shows sender name for other users messages', () => {
    const otherUserMessage = { ...textMessage, sender: 'otheruser' };
    
    render(
      <MessageItem
        message={otherUserMessage}
        currentUser={currentUser}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('otheruser')).toBeInTheDocument();
    expect(screen.getByText('Hello world')).toBeInTheDocument();
  });
});
