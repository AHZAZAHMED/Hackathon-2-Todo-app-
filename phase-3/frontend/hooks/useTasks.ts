/**
 * useTasks hook
 * Custom hook for task management
 */

'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';
import { Task, CreateTaskInput, UpdateTaskInput } from '@/types/task';

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load all tasks
   */
  const loadTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getTasks();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Create a new task
   */
  const createTask = async (input: CreateTaskInput): Promise<Task> => {
    const newTask = await apiClient.createTask(input);
    setTasks([...tasks, newTask]);
    return newTask;
  };

  /**
   * Update an existing task
   */
  const updateTask = async (taskId: number, input: UpdateTaskInput): Promise<Task> => {
    const updatedTask = await apiClient.updateTask(taskId, input);
    setTasks(tasks.map(task => task.id === taskId ? updatedTask : task));
    return updatedTask;
  };

  /**
   * Delete a task
   */
  const deleteTask = async (taskId: number): Promise<void> => {
    await apiClient.deleteTask(taskId);
    setTasks(tasks.filter(task => task.id !== taskId));
  };

  /**
   * Toggle task completion
   */
  const toggleComplete = async (taskId: number): Promise<Task> => {
    const updatedTask = await apiClient.toggleTaskComplete(taskId);
    setTasks(tasks.map(task => task.id === taskId ? updatedTask : task));
    return updatedTask;
  };

  /**
   * Get task statistics
   */
  const getStats = () => {
    const total = tasks.length;
    const completed = tasks.filter(task => task.completed).length;
    const pending = total - completed;
    return { total, completed, pending };
  };

  // Load tasks on mount
  useEffect(() => {
    loadTasks();
  }, []);

  return {
    tasks,
    loading,
    error,
    loadTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
    getStats,
  };
}
