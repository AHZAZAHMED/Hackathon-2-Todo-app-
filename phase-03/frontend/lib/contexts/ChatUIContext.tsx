'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import { ChatUIState, ChatUIContextValue } from '@/types/chat';

const ChatUIContext = createContext<ChatUIContextValue | undefined>(undefined);

export function ChatUIProvider({ children }: { children: React.ReactNode }) {
  const [uiState, setUiState] = useState<ChatUIState>({
    isOpen: false,
    isMinimized: false,
  });

  const openChat = useCallback(() => {
    setUiState({ isOpen: true, isMinimized: false });
  }, []);

  const closeChat = useCallback(() => {
    setUiState({ isOpen: false, isMinimized: false });
  }, []);

  const minimizeChat = useCallback(() => {
    setUiState({ isOpen: false, isMinimized: true });
  }, []);

  const toggleChat = useCallback(() => {
    setUiState((prev) => ({ isOpen: !prev.isOpen, isMinimized: false }));
  }, []);

  return (
    <ChatUIContext.Provider value={{ uiState, openChat, closeChat, minimizeChat, toggleChat }}>
      {children}
    </ChatUIContext.Provider>
  );
}

export function useChatUI(): ChatUIContextValue {
  const context = useContext(ChatUIContext);
  if (!context) {
    throw new Error('useChatUI must be used within ChatUIProvider');
  }
  return context;
}
