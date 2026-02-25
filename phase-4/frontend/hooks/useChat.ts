// frontend/hooks/useChat.ts
'use client';

import { useState, useCallback } from 'react';
import { ChatMessage } from '@/types/chat';
import { sendChatMessage } from '@/lib/chat-client';
import { saveMessages, loadMessages } from '@/lib/chat-storage';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load messages from session storage (for conversation restoration)
   */
  const loadConversation = useCallback(() => {
    const storedMessages = loadMessages();
    const chatMessages: ChatMessage[] = storedMessages.map(msg => ({
      ...msg,
      timestamp: new Date(msg.timestamp),
    }));
    setMessages(chatMessages);
  }, []);

  /**
   * Send a message to the AI assistant
   */
  const sendMessage = useCallback(async (content: string) => {
    // Create user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
      status: 'sending',
      error: null,
    };

    // Add user message to conversation
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Send to backend
      const response = await sendChatMessage(content);

      // Update user message status to sent
      setMessages(prev =>
        prev.map(msg =>
          msg.id === userMessage.id ? { ...msg, status: 'sent' as const } : msg
        )
      );

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response,
        timestamp: new Date(),
        status: 'sent',
        error: null,
      };

      setMessages(prev => {
        const updated = [...prev, assistantMessage];
        // Save to session storage
        saveMessages(
          updated.map(msg => ({
            ...msg,
            timestamp: msg.timestamp.toISOString(),
          }))
        );
        return updated;
      });
    } catch (err: any) {
      // Handle token expiry specially
      if (err.message === 'UNAUTHORIZED') {
        // Save conversation before redirect
        setMessages(prev => {
          saveMessages(
            prev.map(msg => ({
              ...msg,
              timestamp: msg.timestamp.toISOString(),
            }))
          );
          return prev;
        });
        setError('Session expired. Please log in again.');
        // Trigger redirect (handled by ChatProvider)
        throw err;
      }

      // Mark user message as failed
      setMessages(prev =>
        prev.map(msg =>
          msg.id === userMessage.id
            ? { ...msg, status: 'failed' as const, error: err.message }
            : msg
        )
      );

      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Retry a failed message
   */
  const retryMessage = useCallback(async (messageId: string) => {
    const message = messages.find(msg => msg.id === messageId);
    if (!message || message.status !== 'failed') return;

    await sendMessage(message.content);
  }, [messages, sendMessage]);

  /**
   * Clear conversation
   */
  const clearConversation = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    retryMessage,
    clearConversation,
    loadConversation,
  };
}
