import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return `${diffSecs}s ago`;
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
}

export function getStateColor(state: string): string {
  const colors: Record<string, string> = {
    idle: '#6b7280',
    thinking: '#6366f1',
    retrieving_memory: '#06b6d4',
    selecting_playbook: '#10b981',
    generating_agent: '#f59e0b',
    building_output: '#3b82f6',
    reviewing: '#ef4444',
    waiting_approval: '#f97316',
    completed: '#22c55e',
    failed: '#ef4444',
  };
  return colors[state] || '#6b7280';
}

export function getStateLabel(state: string): string {
  const labels: Record<string, string> = {
    idle: 'Idle',
    thinking: 'Thinking...',
    retrieving_memory: 'Retrieving Memory',
    selecting_playbook: 'Selecting Playbook',
    generating_agent: 'Generating Agent',
    building_output: 'Building Output',
    reviewing: 'Reviewing',
    waiting_approval: 'Awaiting Approval',
    completed: 'Completed',
    failed: 'Failed',
  };
  return labels[state] || state;
}
