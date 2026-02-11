// frontend/components/chat/ChatProvider.tsx
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useChat } from '@/hooks/useChat';
import { useChatAuth } from '@/hooks/useChatAuth';
import { useTasks } from '@/contexts/TasksContext';
import { saveChatState, loadChatState } from '@/lib/chat-storage';

interface ChatContextValue {
  isOpen: boolean;
  toggleChat: () => void;
  openChat: () => void;
  closeChat: () => void;
  messages: ReturnType<typeof useChat>['messages'];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  retryMessage: (messageId: string) => Promise<void>;
  clearConversation: () => void;
}

const ChatContext = createContext<ChatContextValue | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, redirectToLogin } = useChatAuth();
  const { refreshTasks } = useTasks();
  const {
    messages,
    isLoading,
    error,
    sendMessage: sendChatMessage,
    retryMessage,
    clearConversation,
    loadConversation,
  } = useChat();

  // Load chat state from session storage on mount
  useEffect(() => {
    const savedState = loadChatState();
    if (savedState) {
      setIsOpen(savedState.isOpen);
    }

    // Load conversation if exists
    loadConversation();
  }, [loadConversation]);

  // Save chat state whenever it changes
  useEffect(() => {
    saveChatState(isOpen);
  }, [isOpen]);

  const toggleChat = () => {
    // Check authentication before opening
    if (!isOpen && !isAuthenticated) {
      redirectToLogin();
      return;
    }

    setIsOpen(prev => !prev);
  };

  const openChat = () => {
    // Check authentication before opening
    if (!isAuthenticated) {
      redirectToLogin();
      return;
    }

    setIsOpen(true);
  };

  const closeChat = () => {
    setIsOpen(false);
  };

  const sendMessage = async (content: string) => {
    try {
      await sendChatMessage(content);
      // Refresh task list after successful message to reflect any changes made by the chatbot
      await refreshTasks();
    } catch (err: any) {
      // Handle unauthorized error (token expiry)
      if (err.message === 'UNAUTHORIZED') {
        redirectToLogin();
      }
    }
  };

  const value: ChatContextValue = {
    isOpen,
    toggleChat,
    openChat,
    closeChat,
    messages,
    isLoading,
    error,
    sendMessage,
    retryMessage,
    clearConversation,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChatContext() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChatContext must be used within ChatProvider');
  }
  return context;
}
