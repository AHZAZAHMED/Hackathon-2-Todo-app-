// frontend/components/chat/ChatMessage.tsx
'use client';

import { ChatMessage as ChatMessageType } from '@/types/chat';

interface ChatMessageProps {
  message: ChatMessageType;
  onRetry?: (messageId: string) => void;
}

export function ChatMessage({ message, onRetry }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isFailed = message.status === 'failed';
  const isSending = message.status === 'sending';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-900'
        } ${isFailed ? 'border-2 border-red-500' : ''}`}
      >
        <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>

        {isSending && (
          <div className="flex items-center mt-1 text-xs opacity-70">
            <div className="animate-pulse">Sending...</div>
          </div>
        )}

        {isFailed && (
          <div className="mt-2 flex items-center gap-2">
            <span className="text-xs text-red-600">Failed to send</span>
            {onRetry && (
              <button
                onClick={() => onRetry(message.id)}
                className="text-xs text-blue-600 hover:text-blue-800 underline"
              >
                Retry
              </button>
            )}
          </div>
        )}

        {message.error && (
          <div className="mt-1 text-xs text-red-600">
            {message.error}
          </div>
        )}
      </div>
    </div>
  );
}
