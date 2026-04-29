# BLUEPRINT — Ismael Agent World v2

## One-line definition
A production-grade personal AI operating system: a Next.js command-centre UI backed by a real Python execution engine, persistent memory, live tool integrations, and an autonomous multi-agent orchestration loop — replacing Claude, ChatGPT, Perplexity, and GitHub Copilot with a single private interface.

---

## What this IS (not a concept — a real system)

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI / Dashboard | Next.js 15 App Router + shadcn/ui + Framer Motion | Command centre, real-time agent status, logs |
| API Gateway | Next.js Route Handlers (edge-ready) | Bridge between UI and Python execution engine |
| Execution Engine | Python FastAPI (Railway) | Real agent workers, tool calls, task queue |
| Agent Workers | Python classes with execute() contract | Each agent has tools access, memory access, I/O contract |
| Tool Layer | Python modules | Web search, code execution, file ops, API caller, browser |
| Memory System | Supabase pgvector + structured logs | Session memory, long-term learning, semantic retrieval |
| Task Queue | FastAPI BackgroundTasks → Redis (Phase 2) | Async execution, retries, dependency chains |
| Real-time | Supabase Realtime channels | Live agent state pushed to UI without polling |
| Auth | Supabase Auth | Single-user private access |
| Payments | Lemon Squeezy | When commercialised |
| Deployment | Vercel (web) + Railway (api) | Zero-ops |

---

## What was missing (now fixed in this blueprint)

| Gap from audit | Fix |
|----------------|-----|
| Orchestration engine | FastAPI orchestrator with task decomposition, routing, retries |
| Tool execution | Real tools: Serper search, Python subprocess, file R/W, HTTP caller |
| Memory system | Supabase pgvector + JSON session logs + cross-agent knowledge sharing |
| Real agent workers | Python classes: each has role, tools, memory, input/output contract |
| Task lifecycle | task_id, status, dependencies, retries, failure handling |
| Feedback loop | After each task: log result → extract learning → store in memory |
| Multi-agent flow | Planner → Router → Specialists → Reviewer → Memory Writer |
| UI / dashboard | 7 pages with real-time data from Supabase |
| Deployment | Vercel + Railway + docker-compose for local dev |
| Self-improvement | Memory Agent stores learnings; repeated patterns → permanent playbooks |

---

## Repository Structure

```
ismael-agent-world/
├── apps/
│   ├── web/                          # Next.js 15 command centre
│   │   ├── app/
│   │   │   ├── layout.tsx            # Root layout, dark theme, auth guard
│   │   │   ├── page.tsx              # Redirect → /command
│   │   │   ├── command/page.tsx      # Main orb + request input
│   │   │   ├── agents/page.tsx       # Agent node grid with live state
│   │   │   ├── projects/page.tsx     # Project workspace
│   │   │   ├── memory/page.tsx       # Memory vault browser
│   │   │   ├── playbooks/page.tsx    # Playbook library
│   │   │   ├── approvals/page.tsx    # Approval queue
│   │   │   └── logs/page.tsx         # Execution log stream
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn/ui base components
│   │   │   ├── agents/               # AgentCard, AgentOrb, AgentGrid
│   │   │   ├── command/              # CommandInput, ResponsePanel
│   │   │   ├── logs/                 # LogStream, LogEntry
│   │   │   ├── memory/               # MemoryCard, DomainCapsule
│   │   │   └── layout/               # Sidebar, Header, ThemeProvider
│   │   ├── lib/
│   │   │   ├── supabase.ts           # Supabase client
│   │   │   ├── api.ts                # FastAPI client (typed fetch wrappers)
│   │   │   └── types.ts              # Shared TypeScript types (mirrored from packages/types)
│   │   └── app/api/
│   │       ├── run/route.ts          # POST /api/run → forwards to FastAPI
│   │       └── status/[id]/route.ts  # GET /api/status/:id → FastAPI
│   │
│   └── api/                          # Python FastAPI execution engine
│       ├── main.py                   # FastAPI app, CORS, routes
│       ├── orchestrator.py           # Task decomposition + agent routing
│       ├── agents/
│       │   ├── base.py               # BaseAgent(role, tools, memory, execute())
│       │   ├── chief.py              # ChiefAgent — entry point, final response
│       │   ├── intent_router.py      # IntentRouterAgent — classify request
│       │   ├── knowledge.py          # KnowledgeAgent — semantic memory retrieval
│       │   ├── playbook.py           # PlaybookAgent — select or create workflow
│       │   ├── dynamic_generator.py  # DynamicAgentGenerator — spawn specialists
│       │   ├── builder.py            # BuilderAgent — produce structured output
│       │   ├── critic.py             # CriticAgent — review and QA output
│       │   ├── memory_writer.py      # MemoryAgent — extract + persist learnings
│       │   └── approval.py           # ApprovalAgent — flag risky actions
│       ├── tools/
│       │   ├── base.py               # BaseTool interface
│       │   ├── web_search.py         # Serper API web search
│       │   ├── code_executor.py      # Safe Python subprocess execution
│       │   ├── file_ops.py           # File read/write/list
│       │   ├── http_caller.py        # Generic HTTP API caller
│       │   └── supabase_tool.py      # Supabase query tool
│       ├── memory/
│       │   ├── store.py              # MemoryStore: save/retrieve/embed
│       │   ├── embeddings.py         # OpenAI text-embedding-3-small
│       │   └── schemas.py            # Memory, DomainCapsule, Playbook schemas
│       ├── tasks/
│       │   ├── queue.py              # Task queue (in-memory → Redis Phase 2)
│       │   ├── lifecycle.py          # TaskStatus, retry logic, dependency checks
│       │   └── feedback.py           # Post-task: extract learning, store in memory
│       └── config.py                 # Env vars, model routing, constants
│
├── packages/
│   └── types/                        # Shared TypeScript type definitions
│       ├── index.ts
│       └── agents.ts
│
├── turbo.json                        # Turborepo config
├── pnpm-workspace.yaml               # pnpm workspaces
├── package.json                      # Root package.json
├── docker-compose.yml                # Local dev: api + redis + supabase
└── .env.example                      # All required env vars documented
```

---

## Agent Execution Contract

Every agent in `apps/api/agents/` must implement this interface:

```python
class BaseAgent:
    role: str           # e.g. "intent_router"
    description: str    # What this agent does
    tools: list[str]    # Tool names this agent can use
    memory_access: bool # Can this agent read/write memory?

    async def execute(
        self,
        task_packet: TaskPacket,
        context: AgentContext,
    ) -> AgentResult:
        # Returns: output, confidence, next_agent, memory_updates, logs
        ...
```

---

## Tool Execution Contract

Every tool in `apps/api/tools/` must implement:

```python
class BaseTool:
    name: str
    description: str

    async def run(self, input: dict) -> ToolResult:
        # Returns: output, success, error, metadata
        ...
```

---

## Memory System

Three tiers:

1. **Session memory** (in-memory dict, cleared after session)
   - Current task context
   - Recent agent outputs
   - Handoff data between agents

2. **Long-term memory** (Supabase pgvector)
   - Domain capsules (learnings per domain)
   - Playbooks (successful workflows)
   - Preferences (user-specific patterns)
   - Similarity search via pgvector

3. **Cross-agent knowledge** (Supabase structured tables)
   - Agent run history
   - Tool usage logs
   - Error patterns + fixes

---

## Task Lifecycle

```
CREATED → QUEUED → RUNNING → [WAITING_APPROVAL] → COMPLETED
                           ↘ FAILED → RETRYING → COMPLETED/DEAD
```

Every task has:
- `task_id` (UUID)
- `parent_task_id` (for sub-tasks)
- `agent_id` (which agent owns it)
- `status` (enum above)
- `retry_count` (max 3)
- `dependencies` (list of task_ids that must complete first)
- `result` (structured output)
- `error` (if failed)
- `created_at`, `started_at`, `completed_at`

---

## Command Flow (Full Stack)

```
User types request in /command
  ↓ POST /api/run (Next.js route handler)
  ↓ FastAPI /run endpoint
  ↓ ChiefAgent.execute()
  ↓ IntentRouterAgent.execute()     ← classifies domain + request type
  ↓ KnowledgeAgent.execute()        ← semantic search in memory
  ↓ PlaybookAgent.execute()         ← select or generate playbook
  ↓ DynamicAgentGenerator.execute() ← spawn specialist agents if needed
  ↓ BuilderAgent.execute()          ← produce structured output
  ↓ CriticAgent.execute()           ← QA and weakness check
  ↓ MemoryAgent.execute()           ← extract + store learnings
  ↓ ApprovalAgent.execute()         ← flag if risky action detected
  ↓ ChiefAgent final response
  ↓ Supabase Realtime broadcast
  ↓ Next.js UI updates live
```

---

## Feedback Loop

After every completed task, `tasks/feedback.py` runs:
1. Extract key learnings from agent result
2. Generate embedding (OpenAI text-embedding-3-small)
3. Store in `memories` table with domain + confidence
4. If same domain appears 3+ times → promote to permanent playbook
5. If task failed → store error pattern for future avoidance

---

## Supabase Schema

```sql
-- Agent runs
create table agent_runs (
  id uuid primary key default gen_random_uuid(),
  task_id uuid not null,
  agent_role text not null,
  status text not null,
  input jsonb,
  output jsonb,
  duration_ms int,
  created_at timestamptz default now()
);

-- Memory (pgvector)
create extension if not exists vector;
create table memories (
  id uuid primary key default gen_random_uuid(),
  domain text not null,
  content text not null,
  embedding vector(1536),
  memory_type text, -- 'learning' | 'playbook' | 'preference' | 'error_pattern'
  confidence float default 1.0,
  use_count int default 0,
  created_at timestamptz default now()
);

-- Tasks
create table tasks (
  id uuid primary key default gen_random_uuid(),
  parent_id uuid references tasks(id),
  title text not null,
  status text not null default 'created',
  agent_id text,
  input jsonb,
  result jsonb,
  error text,
  retry_count int default 0,
  dependencies uuid[],
  created_at timestamptz default now(),
  started_at timestamptz,
  completed_at timestamptz
);

-- Playbooks
create table playbooks (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  domain text not null,
  steps jsonb not null,
  success_count int default 0,
  created_at timestamptz default now()
);

-- Execution logs
create table execution_logs (
  id uuid primary key default gen_random_uuid(),
  task_id uuid references tasks(id),
  agent_role text,
  level text, -- 'info' | 'warn' | 'error'
  message text not null,
  metadata jsonb,
  created_at timestamptz default now()
);
```

---

## Real-time (Supabase Realtime)

Next.js subscribes to these channels:
- `agent_runs` table changes → update AgentCard states live
- `execution_logs` inserts → stream to /logs page
- `tasks` status changes → update /projects page

---

## Environment Variables

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# AI APIs
ANTHROPIC_API_KEY=      # Claude — primary for code gen, reasoning
OPENAI_API_KEY=         # GPT-4o — planning, QA, embeddings
GROK_API_KEY=           # Grok — creative, risk analysis

# Tools
SERPER_API_KEY=         # Web search (serper.dev)

# FastAPI
FASTAPI_URL=            # Railway URL in prod, localhost:8000 in dev
FASTAPI_SECRET=         # Internal API secret between Next.js and FastAPI

# Payments
LEMON_SQUEEZY_API_KEY=
```

---

## UI Design System

- Base: `bg-slate-950` (near-black)
- Accent primary: `#0abf9f` (teal)
- Accent secondary: `#3b82f6` (blue)
- Danger: `#ef4444`
- Text: `text-slate-100` / `text-slate-400`
- Cards: `bg-slate-900 border border-slate-800`
- Animations: Framer Motion only, reflect real agent state
- NOT a generic admin dashboard — private command centre aesthetic
- Orb on /command pulses when agents are running
- Agent nodes in /agents show real-time state with animated rings

---

## Phase Plan

### Phase 1 — Foundation (monorepo + types + API shell + UI shell)
Tasks: monorepo setup, tsconfig, shared types, FastAPI skeleton, Supabase schema, Next.js layout, auth guard, Supabase client

### Phase 2 — Core Agents (real Python execution)
Tasks: BaseAgent + BaseTool, ChiefAgent, IntentRouterAgent, KnowledgeAgent, tool layer (web search + http caller), memory store (pgvector), task queue + lifecycle

### Phase 3 — Full Agent Roster + Feedback Loop
Tasks: PlaybookAgent, DynamicAgentGenerator, BuilderAgent, CriticAgent, MemoryAgent, ApprovalAgent, feedback loop, cross-agent knowledge sharing

### Phase 4 — UI Pages (connected to real data)
Tasks: /command with real execution, /agents with live state, /logs stream, /memory browser, /playbooks library, /approvals queue, /projects workspace

### Phase 5 — Polish + Deploy
Tasks: docker-compose, Railway FastAPI deploy, Vercel env config, error boundaries, loading states, Lemon Squeezy integration

---

## Success Criteria

A 10/10 system means:
- [ ] User types any request in /command → real agent execution happens → response appears
- [ ] /agents shows real-time agent states (idle/thinking/running/completed)
- [ ] Memory persists across sessions — 3rd visit to same domain uses learned playbook
- [ ] Tools actually work: web search returns real results, code executes, APIs are called
- [ ] Task failures auto-retry (max 3) then surface in /approvals
- [ ] Feedback loop stores learnings → memory grows smarter over time
- [ ] Full deploy: Vercel (web) + Railway (api) with zero manual ops

---

*This blueprint is the source of truth. The autonomous orchestrator reads it to plan every PR.*
*Do not edit manually — update by triggering orchestrator with a focus area.*
