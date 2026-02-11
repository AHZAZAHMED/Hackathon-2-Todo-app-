// frontend/lib/chat-client.ts

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  response: string;
}

export interface ChatError {
  error: string;
  message: string;
}

/**
 * Send a chat message to the backend
 * Uses existing api-client.ts which automatically attaches JWT
 */
export async function sendChatMessage(message: string): Promise<string> {
  try {
    // Validate message length (500 character limit)
    if (message.length === 0) {
      throw new Error('Message cannot be empty');
    }
    if (message.length > 500) {
      throw new Error('Message exceeds 500 character limit');
    }

    // Send request via centralized API client
    // Note: We need to extend apiClient to support generic POST requests
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Get auth headers from apiClient's private method by making a request
    const authHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Get JWT token from token exchange endpoint
    try {
      const tokenResponse = await fetch('/api/auth/token', {
        credentials: 'include',
      });

      if (tokenResponse.ok) {
        const data = await tokenResponse.json();
        if (data.token) {
          authHeaders['Authorization'] = `Bearer ${data.token}`;
        }
      }
    } catch (error) {
      console.warn('Failed to get JWT token:', error);
    }

    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: authHeaders,
      credentials: 'include',
      body: JSON.stringify({ message }),
    });

    // Handle specific error cases
    if (response.status === 401) {
      throw new Error('UNAUTHORIZED');
    }

    if (response.status === 422) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Invalid message format');
    }

    if (response.status === 500) {
      throw new Error('Server error. Please try again.');
    }

    if (response.status === 503) {
      throw new Error('Service unavailable. Please try again later.');
    }

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    const data: ChatResponse = await response.json();
    return data.response;
  } catch (error: any) {
    // Re-throw known errors
    if (error.message === 'UNAUTHORIZED' ||
        error.message.includes('character limit') ||
        error.message.includes('cannot be empty')) {
      throw error;
    }

    // Network errors
    if (!navigator.onLine) {
      throw new Error('No internet connection. Please check your network.');
    }

    throw new Error('Unable to send message. Please try again.');
  }
}
