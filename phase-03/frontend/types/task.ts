/**
 * Task entity types
 * Represents a task in the todo application
 */

export interface Task {
  id: number; // Backend returns integer ID
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
}

/**
 * Input type for creating a new task
 */
export interface CreateTaskInput {
  title: string;
  description: string;
}

/**
 * Input type for updating an existing task
 */
export interface UpdateTaskInput {
  title: string; // Required in backend
  description: string; // Required in backend
}
