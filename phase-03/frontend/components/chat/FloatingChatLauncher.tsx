'use client';

import { MessageCircle, X } from 'lucide-react';
import { useChatUI } from '@/lib/contexts/ChatUIContext';
import { ChatInterface } from './ChatInterface';

export function FloatingChatLauncher() {
  const { uiState, toggleChat } = useChatUI();

  return (
    <>
      {/* Floating Icon Button - Always visible, changes icon when chat is open */}
      <button
        onClick={toggleChat}
        className="fixed bottom-6 right-6 z-[60] h-14 w-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all md:h-16 md:w-16"
        aria-label="Open chat"
      >
        {uiState.isOpen ? (
          <X className="h-6 w-6 mx-auto" />
        ) : (
          <MessageCircle className="h-6 w-6 mx-auto" />
        )}
      </button>

      {/* Chat Interface */}
      {uiState.isOpen && <ChatInterface />}
    </>
  );
}
