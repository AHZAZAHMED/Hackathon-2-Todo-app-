'use client';

import { X, Minus } from 'lucide-react';
import { useChatUI } from '@/lib/contexts/ChatUIContext';

export function ChatHeader() {
  const { closeChat, minimizeChat } = useChatUI();

  return (
    <div className="flex items-center justify-between p-4 border-b bg-white rounded-t-lg">
      <h2 className="text-lg font-semibold text-gray-900">Chat Assistant</h2>
      <div className="flex gap-2">
        <button
          onClick={minimizeChat}
          className="p-1 hover:bg-gray-100 rounded transition-colors"
          aria-label="Minimize chat"
        >
          <Minus className="h-5 w-5 text-gray-600" />
        </button>
        <button
          onClick={closeChat}
          className="p-1 hover:bg-gray-100 rounded transition-colors"
          aria-label="Close chat"
        >
          <X className="h-5 w-5 text-gray-600" />
        </button>
      </div>
    </div>
  );
}
