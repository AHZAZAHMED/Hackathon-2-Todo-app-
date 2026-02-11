// frontend/components/chat/ChatWindow.tsx
'use client';

import { useChatContext } from './ChatProvider';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';

export function ChatWindow() {
  const { isOpen, closeChat, messages, isLoading, error, sendMessage, retryMessage } = useChatContext();

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-24 right-5 z-chat-window w-[400px] h-[600px] max-w-[calc(100vw-2.5rem)] max-h-[calc(100vh-8rem)] bg-white rounded-lg shadow-xl flex flex-col md:w-[400px] md:h-[600px]">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-blue-600 text-white rounded-t-lg">
        <div className="flex items-center gap-2">
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
          <h3 className="font-semibold">AI Assistant</h3>
        </div>

        <button
          onClick={closeChat}
          className="hover:bg-blue-700 rounded p-1 transition-colors"
          aria-label="Close chat"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-b border-red-200">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Messages */}
      <ChatMessages messages={messages} isLoading={isLoading} onRetry={retryMessage} />

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
