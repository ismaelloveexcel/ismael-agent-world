// ─────────────────────────────────────────────────────────────
// Ismael Agent World — Shared TypeScript Types
// Single source of truth for UI, API routes, and mock data.
// ─────────────────────────────────────────────────────────────

// ─── Agent ───────────────────────────────────────────────────

export type AgentStatus =
  | 'idle'
  | 'thinking'
  | 'executing'
  | 'waiting_approval'
  | 'success'
  | 'error';

export type AgentRole =
  | 'chief'
  | 'intent_router'
  | 'knowledge'
  | 'playbook'
  | 'dynamic_generator'
  | 'builder'
  | 'critic'
  | 'memory_writer'
  | 'approval';

export interface Agent {
  id: string;
  name: string;
  role: AgentRole;
  status: AgentStatus;
  /** ISO-8601 timestamp of last status change */
  lastActiveAt: string;
  /** Short human-readable description of current activity */
  currentActivity: string | null;
  /** Number of tasks completed across all sessions */
  tasksCompleted: number;
  /** Average execution time in milliseconds */
  avgExecMs: number;
}

// ─── Task ────────────────────────────────────────────────────

export type TaskStatus =
  | 'queued'
  | 'running'
  | 'waiting_approval'
  | 'completed'
  | 'failed'
  | 'cancelled';

export type TaskPriority = 'low' | 'normal' | 'high' | 'critical';

export interface TaskStep {
  stepIndex: number;
  agentRole: AgentRole;
  description: string;
  status: 'pending' | 'running' | 'done' | 'failed';
  startedAt: string | null;
  completedAt: string | null;
  /** Tool called during this step, if any */
  toolUsed: string | null;
}

export interface Task {
  id: string;
  /** Human-readable title derived from the original prompt */
  title: string;
  /** The original raw prompt from the user */
  prompt: string;
  status: TaskStatus;
  priority: TaskPriority;
  /** IDs of tasks that must complete before this one starts */
  dependsOn: string[];
  steps: TaskStep[];
  /** Agent ID currently owning this task */
  assignedAgentId: string | null;
  createdAt: string;
  startedAt: string | null;
  completedAt: string | null;
  /** Number of automatic retries attempted */
  retryCount: number;
  /** Final structured output produced by BuilderAgent */
  output: string | null;
  /** Error message if status === 'failed' */
  errorMessage: string | null;
}

// ─── Log Entry ───────────────────────────────────────────────

export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'success';

export type LogSource =
  | 'orchestrator'
  | AgentRole
  | 'tool'
  | 'memory'
  | 'system';

export interface LogEntry {
  id: string;
  taskId: string | null;
  agentId: string | null;
  level: LogLevel;
  source: LogSource;
  message: string;
  /** Arbitrary structured metadata (tool args, timing, etc.) */
  meta: Record<string, unknown> | null;
  timestamp: string;
}

// ─── Memory ──────────────────────────────────────────────────

export type MemoryType =
  | 'fact'
  | 'preference'
  | 'pattern'
  | 'learning'
  | 'playbook_ref';

export interface MemoryEntry {
  id: string;
  type: MemoryType;
  domain: string;
  /** The actual knowledge content */
  content: string;
  /** Tags for filtering and grouping */
  tags: string[];
  /** Relevance score: 0–1, updated on each retrieval hit */
  relevanceScore: number;
  /** Source task that produced this memory */
  sourceTaskId: string | null;
  createdAt: string;
  lastAccessedAt: string;
  /** How many times this entry was retrieved */
  accessCount: number;
}

export interface DomainCapsule {
  domain: string;
  entryCount: number;
  /** Most recent memory timestamp in this domain */
  lastUpdatedAt: string;
  topTags: string[];
}

// ─── Playbook ─────────────────────────────────────────────────

export type PlaybookStatus = 'draft' | 'active' | 'archived';

export interface PlaybookStep {
  order: number;
  agentRole: AgentRole;
  instruction: string;
  /** Optional tool required for this step */
  requiredTool: string | null;
}

export interface Playbook {
  id: string;
  name: string;
  description: string;
  status: PlaybookStatus;
  /** Intent categories this playbook handles */
  triggers: string[];
  steps: PlaybookStep[];
  /** Times this playbook was selected by PlaybookAgent */
  usageCount: number;
  /** Average success rate across executions: 0–1 */
  successRate: number;
  createdAt: string;
  updatedAt: string;
}

// ─── Approval ────────────────────────────────────────────────

export type ApprovalStatus = 'pending' | 'approved' | 'rejected';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface ApprovalRequest {
  id: string;
  taskId: string;
  agentId: string;
  /** Human-readable description of the action requiring approval */
  actionDescription: string;
  /** Structured payload the agent wants to execute */
  actionPayload: Record<string, unknown>;
  riskLevel: RiskLevel;
  /** Why ApprovalAgent flagged this action */
  riskReason: string;
  status: ApprovalStatus;
  /** User note added on approval or rejection */
  reviewNote: string | null;
  createdAt: string;
  resolvedAt: string | null;
}

// ─── Project ─────────────────────────────────────────────────

export type ProjectStatus = 'active' | 'paused' | 'completed' | 'archived';

export interface Project {
  id: string;
  name: string;
  description: string;
  status: ProjectStatus;
  /** Task IDs belonging to this project */
  taskIds: string[];
  /** Memory domain scoped to this project */
  memoryDomain: string;
  createdAt: string;
  updatedAt: string;
}

// ─── Command ─────────────────────────────────────────────────

export type CommandPhase =
  | 'idle'
  | 'submitted'
  | 'routing'
  | 'executing'
  | 'complete'
  | 'error';

export interface CommandSession {
  id: string;
  prompt: string;
  phase: CommandPhase;
  /** Task spawned by this command */
  taskId: string | null;
  /** Final response text rendered in ResponsePanel */
  response: string | null;
  startedAt: string;
  completedAt: string | null;
}

// ─── System Stats ─────────────────────────────────────────────

export interface SystemStats {
  totalTasksToday: number;
  successRatePercent: number;
  activeAgentCount: number;
  memoryEntryCount: number;
  pendingApprovals: number;
  avgTaskDurationMs: number;
}
