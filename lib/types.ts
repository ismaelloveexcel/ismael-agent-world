export type AgentStatus = 'idle' | 'running' | 'success' | 'error' | 'waiting';

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'blocked';

export type MemoryDomain = 'code' | 'research' | 'planning' | 'communication' | 'system';

export type LogLevel = 'info' | 'warn' | 'error' | 'debug' | 'success';

export interface Agent {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  lastActive: string;
  taskCount: number;
  successRate: number;
  description: string;
  tools: string[];
  avatarInitials: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  assignedAgent: string;
  createdAt: string;
  updatedAt: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  projectId: string | null;
  dependencies: string[];
  retries: number;
}

export interface MemoryEntry {
  id: string;
  domain: MemoryDomain;
  content: string;
  tags: string[];
  createdAt: string;
  agentSource: string;
  relevanceScore: number;
  accessCount: number;
}

export interface LogEntry {
  id: string;
  level: LogLevel;
  message: string;
  agentId: string;
  agentName: string;
  taskId: string | null;
  timestamp: string;
  metadata: Record<string, string | number | boolean>;
}

export interface Playbook {
  id: string;
  name: string;
  description: string;
  steps: string[];
  domain: MemoryDomain;
  usageCount: number;
  createdAt: string;
  successRate: number;
  tags: string[];
}

export interface ApprovalRequest {
  id: string;
  title: string;
  description: string;
  risk: 'low' | 'medium' | 'high';
  requestedBy: string;
  requestedAt: string;
  action: string;
  payload: Record<string, string | number | boolean>;
  status: 'pending' | 'approved' | 'rejected';
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'paused' | 'completed';
  progress: number;
  taskCount: number;
  completedTasks: number;
  createdAt: string;
  agents: string[];
  tags: string[];
}
