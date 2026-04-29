import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { AgentStatus, TaskStatus, LogLevel } from '@/lib/types';

/** Merges Tailwind class names safely, resolving conflicts. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/** Formats an ISO date string into a human-readable relative time label. */
export function relativeTime(isoString: string): string {
  const now = Date.now();
  const then = new Date(isoString).getTime();
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffSec < 60) return `${diffSec}s ago`;
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  return `${diffDay}d ago`;
}

/** Formats an ISO date string as a short readable timestamp. */
export function formatTimestamp(isoString: string): string {
  return new Date(isoString).toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

/** Formats a decimal (0–100) as a percentage string. */
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

/** Maps AgentStatus to Tailwind colour classes for badge/dot rendering. */
export function agentStatusColor(status: AgentStatus): string {
  const map: Record<AgentStatus, string> = {
    idle: 'text-slate-400 bg-slate-800',
    running: 'text-teal-400 bg-teal-950',
    success: 'text-green-400 bg-green-950',
    error: 'text-red-400 bg-red-950',
    waiting: 'text-yellow-400 bg-yellow-950',
  };
  return map[status];
}

/** Maps AgentStatus to a glow/ring Tailwind class for the agent orb. */
export function agentStatusGlow(status: AgentStatus): string {
  const map: Record<AgentStatus, string> = {
    idle: 'ring-slate-700',
    running: 'ring-teal-500 shadow-teal-500/40',
    success: 'ring-green-500 shadow-green-500/40',
    error: 'ring-red-500 shadow-red-500/40',
    waiting: 'ring-yellow-500 shadow-yellow-500/40',
  };
  return map[status];
}

/** Maps TaskStatus to Tailwind colour classes. */
export function taskStatusColor(status: TaskStatus): string {
  const map: Record<TaskStatus, string> = {
    pending: 'text-slate-400 bg-slate-800',
    running: 'text-blue-400 bg-blue-950',
    completed: 'text-green-400 bg-green-950',
    failed: 'text-red-400 bg-red-950',
    blocked: 'text-orange-400 bg-orange-950',
  };
  return map[status];
}

/** Maps LogLevel to Tailwind text colour class. */
export function logLevelColor(level: LogLevel): string {
  const map: Record<LogLevel, string> = {
    info: 'text-slate-300',
    warn: 'text-yellow-400',
    error: 'text-red-400',
    debug: 'text-slate-500',
    success: 'text-teal-400',
  };
  return map[level];
}

/** Maps LogLevel to a short prefix label. */
export function logLevelLabel(level: LogLevel): string {
  const map: Record<LogLevel, string> = {
    info: 'INFO',
    warn: 'WARN',
    error: 'ERR ',
    debug: 'DBG ',
    success: ' OK ',
  };
  return map[level];
}

/** Clamps a number between min and max. */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/** Converts a 0–100 progress value to a CSS width percentage string. */
export function progressWidth(value: number): string {
  return `${clamp(value, 0, 100)}%`;
}

/** Returns initials from a full name string (max 2 chars). */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('');
}

/** Truncates a string to maxLen characters, appending ellipsis if needed. */
export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return `${str.slice(0, maxLen - 1)}…`;
}
