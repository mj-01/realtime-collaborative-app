/**
 * Tests for MessageInput component.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MessageInput } from '../../components/chat/MessageInput';

// Mock the useFileUpload hook
jest.mock('../../hooks/useFileUpload', () => ({
  useFileUpload: () => ({
    isUploading: false,
  }),
}));

describe('MessageInput', () => {
  const mockOnSendMessage = jest.fn();
  const mockOnFileUpload = jest.fn();

  beforeEach(() => {
    mockOnSendMessage.mockClear();
    mockOnFileUpload.mockClear();
  });

  it('renders input field and buttons', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        onFileUpload={mockOnFileUpload}
      />
    );

    expect(screen.getByPlaceholderText('Type a message...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /📎/i })).toBeInTheDocument();
  });

  it('sends message when form is submitted', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        onFileUpload={mockOnFileUpload}
      />
    );

    const input = screen.getByPlaceholderText('Type a message...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Hello world' } });
    fireEvent.click(sendButton);

    expect(mockOnSendMessage).toHaveBeenCalledWith('Hello world');
  });

  it('does not send empty message', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        onFileUpload={mockOnFileUpload}
      />
    );

    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);

    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  it('trims whitespace from message', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        onFileUpload={mockOnFileUpload}
      />
    );

    const input = screen.getByPlaceholderText('Type a message...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: '  Hello world  ' } });
    fireEvent.click(sendButton);

    expect(mockOnSendMessage).toHaveBeenCalledWith('Hello world');
  });

  it('clears input after sending message', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        onFileUpload={mockOnFileUpload}
      />
    );

    const input = screen.getByPlaceholderText('Type a message...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Hello world' } });
    fireEvent.click(sendButton);

    expect(input).toHaveValue('');
  });

  it('handles file upload', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        onFileUpload={mockOnFileUpload}
      />
    );

    const fileInput = screen.getByRole('button', { name: /📎/i });
    const hiddenFileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    fireEvent.change(hiddenFileInput, { target: { files: [file] } });

    expect(mockOnFileUpload).toHaveBeenCalledWith(file);
  });

  it('disables input when disabled prop is true', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        onFileUpload={mockOnFileUpload}
        disabled={true}
      />
    );

    const input = screen.getByPlaceholderText('Type a message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    const fileButton = screen.getByRole('button', { name: /📎/i });

    expect(input).toBeDisabled();
    expect(sendButton).toBeDisabled();
    expect(fileButton).toBeDisabled();
  });
});
