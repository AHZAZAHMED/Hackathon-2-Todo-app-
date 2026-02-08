'use client';

import { useChatKit, ChatKit } from '@openai/chatkit-react';
import { useEffect, useState, useRef } from 'react';
import { ChatHeader } from './ChatHeader';
import { useChatUI } from '@/lib/contexts/ChatUIContext';

export function ChatInterface() {
  const { closeChat } = useChatUI();
  const containerRef = useRef<HTMLDivElement>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch JWT token for ChatKit authentication
  useEffect(() => {
    const fetchToken = async () => {
      try {
        const response = await fetch('/api/auth/token', {
          credentials: 'include',
        });

        if (response.ok) {
          const data = await response.json();
          if (data.token) {
            setToken(data.token);
          }
        }
      } catch (error) {
        console.error('Failed to fetch JWT token for ChatKit:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchToken();
  }, []);

  // Escape key handler
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        closeChat();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [closeChat]);

  // Click-outside handler
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        closeChat();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [closeChat]);

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  const domainKey = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || '';

  // Configure ChatKit with JWT and API endpoint using CustomApiConfig
  const chatKitHook = useChatKit({
    api: {
      url: `${apiBaseUrl}/api/chat`,
      domainKey: domainKey,
      fetch: async (input, init) => {
        // Add JWT token to headers
        const headers = new Headers(init?.headers);
        if (token) {
          headers.set('Authorization', `Bearer ${token}`);
        }
        return fetch(input, { ...init, headers, credentials: 'include' });
      },
    },
  });

  if (loading) {
    return (
      <div
        ref={containerRef}
        className="fixed bottom-0 right-0 left-0 top-0 z-50 bg-white flex flex-col overflow-hidden transition-all duration-300 ease-in-out md:bottom-24 md:right-6 md:left-auto md:top-auto md:w-96 md:max-w-[420px] md:h-[600px] md:max-h-[70vh] md:rounded-xl md:shadow-2xl chat-window"
        role="dialog"
        aria-label="Chat window"
      >
        <ChatHeader />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-gray-500">Loading chat...</div>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="fixed bottom-0 right-0 left-0 top-0 z-50 bg-white flex flex-col overflow-hidden transition-all duration-300 ease-in-out md:bottom-24 md:right-6 md:left-auto md:top-auto md:w-96 md:max-w-[420px] md:h-[600px] md:max-h-[70vh] md:rounded-xl md:shadow-2xl chat-window"
      role="dialog"
      aria-label="Chat window"
    >
      {/* Custom Header with close/minimize buttons */}
      <ChatHeader />

      {/* ChatKit component */}
      <div className="flex-1 overflow-hidden">
        <ChatKit control={chatKitHook.control} className="h-full w-full" />
      </div>
    </div>
  );
}
