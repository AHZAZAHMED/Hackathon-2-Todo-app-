/**
 * TasksContext - Shared task state management
 * Allows multiple components (dashboard, chatbot) to access and update task state
 */
'use client';

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';
import { Task } from '@/types/task';

interface TasksContextValue {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  refreshTasks: () => Promise<void>;
  setTasks: (tasks: Task[]) => void;
}

const TasksContext = createContext<TasksContextValue | undefined>(undefined);

export function TasksProvider({ children }: { children: ReactNode }) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedTasks = await apiClient.getTasks();
      setTasks(fetchedTasks);
    } catch (err) {
      console.error('Failed to load tasks:', err);
      setError('Failed to load tasks. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Load tasks on mount
  useEffect(() => {
    refreshTasks();
  }, [refreshTasks]);

  const value: TasksContextValue = {
    tasks,
    loading,
    error,
    refreshTasks,
    setTasks,
  };

  return <TasksContext.Provider value={value}>{children}</TasksContext.Provider>;
}

export function useTasks() {
  const context = useContext(TasksContext);
  if (context === undefined) {
    throw new Error('useTasks must be used within TasksProvider');
  }
  return context;
}
