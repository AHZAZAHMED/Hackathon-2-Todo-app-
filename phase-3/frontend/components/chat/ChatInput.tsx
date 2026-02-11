// frontend/components/chat/ChatInput.tsx
'use client';

import { useState, FormEvent, KeyboardEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

const MAX_CHARACTERS = 500;

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const remainingChars = MAX_CHARACTERS - message.length;
  const isOverLimit = remainingChars < 0;
  const canSend = message.trim().length > 0 && !isOverLimit && !disabled;

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (canSend) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (canSend) {
        onSend(message.trim());
        setMessage('');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4">
      <div className="flex flex-col gap-2">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={disabled}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          rows={3}
          maxLength={MAX_CHARACTERS}
        />

        <div className="flex items-center justify-between">
          <span
            className={`text-xs ${
              isOverLimit
                ? 'text-red-600 font-semibold'
                : remainingChars < 50
                ? 'text-orange-600'
                : 'text-gray-500'
            }`}
          >
            {remainingChars} characters remaining
          </span>

          <button
            type="submit"
            disabled={!canSend}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors text-sm font-medium"
          >
            Send
          </button>
        </div>
      </div>
    </form>
  );
}
