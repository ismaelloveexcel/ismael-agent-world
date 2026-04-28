export type AgentState =
  | 'idle'
  | 'thinking'
  | 'retrieving_memory'
  | 'selecting_playbook'
  | 'generating_agent'
  | 'building_output'
  | 'reviewing'
  | 'waiting_approval'
  | 'completed'
  | 'failed';

export interface Agent {
  id: string;
  name: string;
  role: string;
  description: string;
  state: AgentState;
  capabilities: string[];
  color: string;
  icon: string;
  createdAt: string;
}

export interface DynamicAgent {
  id: string;
  name: string;
  role: string;
  parentAgentId: string;
  playbookId: string;
  state: AgentState;
  taskId: string;
  createdAt: string;
  expiresAt: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'paused' | 'completed' | 'failed';
  agentIds: string[];
  playbookId?: string;
  progress: number;
  createdAt: string;
  updatedAt: string;
  tags: string[];
}

export interface Task {
  id: string;
  projectId?: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'waiting_approval';
  assignedAgentId?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TaskPacket {
  id: string;
  taskId: string;
  fromAgentId: string;
  toAgentId: string;
  payload: Record<string, unknown>;
  handoffTime: string;
}

export interface AgentRun {
  id: string;
  agentId: string;
  taskId: string;
  state: AgentState;
  startTime: string;
  endTime?: string;
  result?: string;
  error?: string;
}

export interface Memory {
  id: string;
  agentId: string;
  content: string;
  tags: string[];
  embedding?: number[];
  relevanceScore: number;
  createdAt: string;
  projectId?: string;
}

export interface Playbook {
  id: string;
  name: string;
  description: string;
  steps: PlaybookStep[];
  domain: string;
  usageCount: number;
  createdAt: string;
}

export interface PlaybookStep {
  id: string;
  order: number;
  agentRole: string;
  action: string;
  description: string;
  requiresApproval: boolean;
}

export interface Approval {
  id: string;
  taskId: string;
  requestedBy: string;
  reason: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'approved' | 'rejected';
  payload: Record<string, unknown>;
  createdAt: string;
  resolvedAt?: string;
}

export interface ExecutionLog {
  id: string;
  agentId: string;
  agentName: string;
  action: string;
  status: 'success' | 'error' | 'warning' | 'info';
  message: string;
  metadata?: Record<string, unknown>;
  timestamp: string;
}

export interface ToolRegistryItem {
  id: string;
  name: string;
  description: string;
  category: string;
  parameters: Record<string, unknown>;
  isEnabled: boolean;
  isSafe: boolean;
  requiresApproval: boolean;
}

export interface ActivityEntry {
  id: string;
  agentId: string;
  agentName: string;
  message: string;
  type: 'handoff' | 'memory' | 'playbook' | 'approval' | 'complete' | 'error' | 'thinking';
  timestamp: string;
}
