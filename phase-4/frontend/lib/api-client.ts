/**
 * API Client
 * Centralized API client for backend communication with Better Auth integration
 */

import { Task, CreateTaskInput, UpdateTaskInput } from '@/types/task';
import { ApiResponse } from '@/types/api';

/**
 * Custom API Error class
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Request configuration interface
 */
interface RequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: unknown;
}

/**
 * API Client class with Better Auth integration
 */
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get authentication headers with JWT token from Better Auth session
   */
  private async getAuthHeaders(): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Get JWT token from our token exchange endpoint
    try {
      const response = await fetch('/api/auth/token', {
        credentials: 'include', // Include Better Auth session cookie
      });

      if (response.ok) {
        const data = await response.json();
        if (data.token) {
          headers['Authorization'] = `Bearer ${data.token}`;
        }
      }
    } catch (error) {
      // Session not available - continue without auth header
      console.warn('Failed to get JWT token:', error);
    }

    return headers;
  }

  /**
   * Generic request method with error handling
   */
  private async request<T>(endpoint: string, config: RequestConfig): Promise<T> {
    const authHeaders = await this.getAuthHeaders();
    const headers: Record<string, string> = {
      ...authHeaders,
      ...config.headers,
    };

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: config.method,
        headers,
        body: config.body ? JSON.stringify(config.body) : undefined,
        credentials: 'include', // Include cookies for session persistence
      });

      // Handle 401 Unauthorized - Token expired or invalid
      if (response.status === 401) {
        // Store original URL for session restoration
        if (typeof window !== 'undefined') {
          const currentPath = window.location.pathname;
          sessionStorage.setItem('redirectAfterLogin', currentPath);
          window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
        }
        throw new ApiError('Unauthorized. Please log in again.', 401);
      }

      // Handle 429 Too Many Requests - Rate limit exceeded
      if (response.status === 429) {
        let errorMessage = 'Too many requests. Please try again later.';
        let retryAfter: number | undefined;

        try {
          const errorData = await response.json();
          if (errorData.error?.message) {
            errorMessage = errorData.error.message;
          }
          if (errorData.error?.retryAfter) {
            retryAfter = errorData.error.retryAfter;
            const minutes = Math.ceil(errorData.error.retryAfter / 60);
            errorMessage = `Too many failed attempts. Please try again in ${minutes} minute${minutes > 1 ? 's' : ''}.`;
          }
        } catch {
          // Use default message if parsing fails
        }

        throw new ApiError(errorMessage, 429, retryAfter ? { retryAfter } : undefined);
      }

      // Handle other non-OK responses
      if (!response.ok) {
        let errorMessage = 'An error occurred';
        let errorDetails: Record<string, unknown> | undefined;

        try {
          const errorData = await response.json();
          errorMessage = errorData.error?.message || errorData.message || errorMessage;
          errorDetails = errorData;
        } catch {
          // If response is not JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }

        throw new ApiError(errorMessage, response.status, errorDetails);
      }

      // Handle empty responses (e.g., 204 No Content)
      if (response.status === 204) {
        return {} as T;
      }

      return await response.json();
    } catch (error) {
      // Re-throw ApiError as-is
      if (error instanceof ApiError) {
        throw error;
      }

      // Handle network errors
      if (error instanceof TypeError) {
        throw new ApiError('Network error. Please check your connection.', 0);
      }

      // Handle other errors
      throw new ApiError('An unexpected error occurred', 0);
    }
  }

  // ==================== Task Endpoints ====================

  /**
   * Get all tasks for the authenticated user
   */
  async getTasks(): Promise<Task[]> {
    const response = await this.request<ApiResponse<Task[]>>('/tasks/', {
      method: 'GET',
    });
    return response.data;
  }

  /**
   * Get a single task by ID
   */
  async getTask(taskId: number): Promise<Task> {
    const response = await this.request<ApiResponse<Task>>(`/tasks/${taskId}`, {
      method: 'GET',
    });
    return response.data;
  }

  /**
   * Create a new task
   */
  async createTask(input: CreateTaskInput): Promise<Task> {
    const response = await this.request<ApiResponse<Task>>('/tasks/', {
      method: 'POST',
      body: input,
    });
    return response.data;
  }

  /**
   * Update an existing task (title and description)
   */
  async updateTask(taskId: number, input: UpdateTaskInput): Promise<Task> {
    const response = await this.request<ApiResponse<Task>>(`/tasks/${taskId}`, {
      method: 'PUT',
      body: input,
    });
    return response.data;
  }

  /**
   * Toggle task completion status
   */
  async toggleTaskComplete(taskId: number): Promise<Task> {
    const response = await this.request<ApiResponse<Task>>(`/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
    return response.data;
  }

  /**
   * Delete a task
   */
  async deleteTask(taskId: number): Promise<void> {
    await this.request<void>(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }
}

// Export singleton instance
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
export const apiClient = new ApiClient(API_BASE_URL);
