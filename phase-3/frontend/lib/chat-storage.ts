// frontend/lib/chat-storage.ts

const CHAT_STATE_KEY = 'chatkit_state';
const CHAT_MESSAGES_KEY = 'chatkit_messages';

export interface ChatStorageState {
  isOpen: boolean;
}

export interface StoredMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  status: 'sending' | 'sent' | 'failed';
  error: string | null;
}

/**
 * Save chat window open/closed state
 */
export function saveChatState(isOpen: boolean): void {
  try {
    const state: ChatStorageState = { isOpen };
    sessionStorage.setItem(CHAT_STATE_KEY, JSON.stringify(state));
  } catch (error) {
    console.error('Failed to save chat state:', error);
  }
}

/**
 * Load chat window open/closed state
 */
export function loadChatState(): ChatStorageState | null {
  try {
    const data = sessionStorage.getItem(CHAT_STATE_KEY);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('Failed to load chat state:', error);
    return null;
  }
}

/**
 * Save conversation messages (for token expiry preservation)
 */
export function saveMessages(messages: StoredMessage[]): void {
  try {
    sessionStorage.setItem(CHAT_MESSAGES_KEY, JSON.stringify(messages));
  } catch (error) {
    console.error('Failed to save messages:', error);
  }
}

/**
 * Load conversation messages
 */
export function loadMessages(): StoredMessage[] {
  try {
    const data = sessionStorage.getItem(CHAT_MESSAGES_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to load messages:', error);
    return [];
  }
}

/**
 * Clear all chat storage (on logout or conversation reset)
 */
export function clearChatStorage(): void {
  try {
    sessionStorage.removeItem(CHAT_STATE_KEY);
    sessionStorage.removeItem(CHAT_MESSAGES_KEY);
  } catch (error) {
    console.error('Failed to clear chat storage:', error);
  }
}
