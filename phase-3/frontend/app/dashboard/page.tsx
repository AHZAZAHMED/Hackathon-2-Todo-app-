/**
 * Dashboard page
 * Main dashboard with task statistics and task list
 * Protected by middleware - only authenticated users can access
 */

'use client';

import { useAuth } from '@/hooks/useAuth';
import { StatsCards } from '@/components/dashboard/StatsCards';
import { TaskList } from '@/components/dashboard/TaskList';
import { useTasks } from '@/contexts/TasksContext';

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const { tasks, loading, error, setTasks } = useTasks();

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.name || 'User'}!
          </h1>
          <p className="mt-2 text-gray-600">Manage your tasks and track your progress</p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <StatsCards tasks={tasks} />

        <div className="mt-8">
          <TaskList tasks={tasks} setTasks={setTasks} />
        </div>
      </div>
    </div>
  );
}
