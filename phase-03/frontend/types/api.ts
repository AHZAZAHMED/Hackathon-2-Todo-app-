/**
 * API response types
 * Standard response formats from the backend API
 */

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

/**
 * API error response
 */
export interface ApiError {
  message: string;
  status: number;
  details?: Record<string, unknown>;
}

/**
 * Paginated API response
 */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
