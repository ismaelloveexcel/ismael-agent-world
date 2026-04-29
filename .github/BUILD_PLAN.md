# Ismael Agent World — Master Build Plan
Generated: 2026-04-29T05:21:24.856026+00:00
By: GPT-4o → Claude (validation) → Grok (risk)

## Grok Risk Notes
As a senior engineer reviewing this build plan and addressing the architectural risks for a solo non-technical developer, here are the top 3 concerns with concise explanations and mitigations:

1. **Scope Creep and Over-Complexity**  
   **Risk**: A non-technical developer may struggle to define clear boundaries for the project, leading to an overly complex system with unnecessary features.  
   **Impact**: Delays, frustration, and potential project abandonment.  
   **Mitigation**: Focus on a minimal viable product (MVP) with only core features. Break tasks into smaller, well-defined deliverables (as started in the plan) and prioritize iterative development over perfection.

2. **Lack of Technical Expertise in Debugging and Optimization**  
   **Risk**: Without deep technical knowledge, the developer may encounter issues in TypeScript/Node setup, dependency conflicts, or performance bottlenecks without knowing how to resolve them.  
   **Impact**: Stalled progress and unreliable application behavior.  
   **Mitigation**: Use well-documented tools and frameworks (e.g., TypeScript with strict defaults, popular libraries). Leverage community resources like Stack Overflow and tutorials. Consider pre-built templates or starter kits to minimize custom configurations.

3. **Dependency Management and Maintenance**  
   **Risk**: A non-technical developer may not fully understand dependency updates, versioning, or security vulnerabilities, leading to outdated or insecure packages.  
   **Impact**: System instability or security breaches over time.  
   **Mitigation**: Use tools like `npm audit`

---

## Summary
Total tasks: 28. Key improvements: split oversized tasks (Command Page, Agent Grid, Layout), added missing Supabase schema and environment config tasks, reordered so shared components precede pages that consume them, added Theme Provider as a discrete task before Layout, ensured every Phase 1 task is deployable in isolation with mock data, and moved Auth before pages that require session guards.

---

## Task 1: Environment Configuration | Phase: 1 | Files: ["package.json", "tsconfig.json", ".gitignore", ".env.example"] | Depends on: None [DONE]
- Configure TypeScript, Node environment, and monorepo workspace settings.
- Define all essential dependencies (Next.js 15, shadcn/ui, Framer Motion, Supabase client).
- Add `.env.example` listing every required environment variable so each subsequent task can reference it.
- Ensure `.gitignore` excludes secrets, build artifacts, and Python virtualenvs.

## Task 2: Define Shared Types | Phase: 1 | Files: ["apps/web/lib/types.ts"] | Depends on: Task 1
- Establish all shared TypeScript interfaces: `Task`, `TaskStatus`, `Agent`, `AgentStatus`, `MemoryEntry`, `Playbook`, `LogEntry`, `ApprovalItem`, `Project`, `ApiResponse<T>`.
- These types are the single source of truth consumed by every component, page, and API route.
- No runtime logic — pure type declarations only.

## Task 3: Mock Data | Phase: 1 | Files: ["apps/web/lib/mock-data.ts"] | Depends on: Task 2
- Implement fully typed mock datasets for every entity defined in `types.ts`: agents, tasks, memory entries, playbooks, logs, approvals, projects.
- Mock data must satisfy all TypeScript interfaces so pages render without a live backend.
- Export named constants (`MOCK_AGENTS`, `MOCK_TASKS`, etc.) for direct import in pages and components.

## Task 4: API Client | Phase: 1 | Files: ["apps/web/lib/api.ts"] | Depends on: Task 3
- Implement a typed `apiClient` with functions: `runTask()`, `getTaskStatus()`, `getAgents()`, `getMemory()`, `getPlaybooks()`, `getLogs()`, `getApprovals()`, `getProjects()`.
- Each function returns mock data in Phase 1 and will swap to real `fetch` calls pointing at FastAPI in Phase 2 — the call signature must not change.
- Include a `BASE_URL` env-var toggle (`NEXT_PUBLIC_API_URL`) so the swap is a config change only.

## Task 5: Supabase Client | Phase: 1 | Files: ["apps/web/lib/supabase.ts"] | Depends on: Task 1
- Initialise the Supabase browser client using `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
- Export typed helpers: `supabase` singleton, `getSession()`, `signIn()`, `signOut()`.
- Keep this file free of UI logic so it can be imported in both client and server contexts.

## Task 6: Theme Provider | Phase: 1 | Files: ["apps/web/components/providers/ThemeProvider.tsx"] | Depends on: Task 1
- Wrap the app in a `next-themes` dark-mode provider defaulting to `"dark"`.
- Export `ThemeProvider` as a named client component.
- No page or layout dependency yet — standalone provider component only.

## Task 7: Root Layout | Phase: 1 | Files: ["apps/web/app/layout.tsx", "apps/web/app/globals.css"] | Depends on: Task 5, Task 6
- Create the root `RootLayout` server component wrapping every page.
- Mount `ThemeProvider`, set `<html lang="en" suppressHydrationWarning>`, apply global CSS resets and CSS variables for the dark theme.
- Include an auth-guard: redirect unauthenticated users to `/login` using `getSession()` from the Supabase client.
- `globals.css` defines only CSS custom properties and Tailwind base layers — no component styles.

## Task 8: Sidebar Navigation | Phase: 1 | Files: ["apps/web/components/layout/Sidebar.tsx"] | Depends on: Task 2, Task 6
- Build a responsive sidebar listing seven nav items: Command, Agents, Projects, Memory, Playbooks, Approvals, Logs.
- Use Next.js `<Link>` with `usePathname()` to highlight the active route.
- Accept no props — all nav items are hardcoded so the component is self-contained and testable.

## Task 9: Header Component | Phase: 1 | Files: ["apps/web/components/layout/Header.tsx"] | Depends on: Task 5, Task 8
- Display current user email from `getSession()`, a sign-out button wired to `signOut()`, and a global system status badge.
- Accept an optional `title` prop for page-level headings rendered inside the header bar.
- Client component only — no server-side data fetching.

## Task 10: Dashboard Shell | Phase: 1 | Files: ["apps/web/app/(dashboard)/layout.tsx", "apps/web/app/page.tsx"] | Depends on: Task 8, Task 9
- Create the `(dashboard)` route group layout that composes `Sidebar` + `Header` + `<main>` content slot.
- `apps/web/app/page.tsx` is a one-line redirect to `/command`.
- This shell is the only place `Sidebar` and `Header` are mounted, keeping page files clean.

## Task 11: Command Input Component | Phase: 1 | Files: ["apps/web/components/command/CommandInput.tsx"] | Depends on: Task 2, Task 4
- Controlled textarea with a submit button.
- On submit, calls `apiClient.runTask()` and emits `onTaskCreated(taskId: string)` to the parent.
- Displays a loading spinner while the request is in flight.
- Fully self-contained — no page-level state required to render.

## Task 12: Response Panel Component | Phase: 1 | Files: ["apps/web/components/command/ResponsePanel.tsx"] | Depends on: Task 2
- Accepts `task: Task | null` prop and renders status, output, and agent chain used.
- Uses Framer Motion fade-in for result appearance.
- Renders a skeleton placeholder when `task` is null.

## Task 13: Command Page | Phase: 1 | Files: ["apps/web/app/(dashboard)/command/page.tsx"] | Depends on: Task 11, Task 12
- Composes `CommandInput` and `ResponsePanel` with local `useState` wiring `onTaskCreated` to load mock task data via `apiClient.getTaskStatus()`.
- The animated orb (Framer Motion pulsing circle) sits above the input as a visual centrepiece.
- No server-side data fetching required.

## Task 14: Agent Card Component | Phase: 1 | Files: ["apps/web/components/agents/AgentCard.tsx"] | Depends on: Task 2
- Accepts `agent: Agent` prop and renders name, role, status badge (idle/running/error), and last-active timestamp.
- Status badge colour is driven by `AgentStatus` enum — no hardcoded strings.
- Framer Motion hover scale animation included.

## Task 15: Agent Grid Component | Phase: 1 | Files: ["apps/web/components/agents/AgentGrid.tsx"] | Depends on: Task 14
- Accepts `agents: Agent[]` prop and renders a responsive CSS grid of `AgentCard` components.
- Renders an empty-state message when the array is empty.
- No data fetching — purely presentational.

## Task 16: Agents Page | Phase: 1 | Files: ["apps/web/app/(dashboard)/agents/page.tsx"] | Depends on: Task 4, Task 15
- Fetches agents via `apiClient.getAgents()` (returns mock data in Phase 1).
- Passes result to `AgentGrid`.
- Includes a page-level refresh button that re-fetches without full navigation.

## Task 17: Memory Card Component | Phase: 1 | Files: ["apps/web/components/memory/MemoryCard.tsx"] | Depends on: Task 2
- Accepts `entry: MemoryEntry` prop and renders content snippet, source agent, timestamp, and relevance score.
- Includes a copy-to-clipboard button.

## Task 18: Memory Page | Phase: 1 | Files: ["apps/web/app/(dashboard)/memory/page.tsx"] | Depends on: Task 4, Task 17
- Fetches memory entries via `apiClient.getMemory()`.
- Renders a search input that client-side filters entries by content.
- Maps filtered results to `MemoryCard` components.

## Task 19: Projects Page | Phase: 1 | Files: ["apps/web/app/(dashboard)/projects/page.tsx", "apps/web/components/projects/ProjectCard.tsx"] | Depends on: Task 4, Task 10
- `ProjectCard` accepts `project: Project` and renders title, description, task count, and status.
- Projects page fetches via `apiClient.getProjects()` and renders a grid of `ProjectCard` components.
- Both files are small enough to remain in the same task (estimated ≤120 lines combined).

## Task 20: Playbooks Page | Phase: 1 | Files: ["apps/web/app/(dashboard)/playbooks/page.tsx", "apps/web/components/playbooks/PlaybookCard.tsx"] | Depends on: Task 4, Task 10
- `PlaybookCard` accepts `playbook: Playbook` and renders name, trigger type, step count, and a run button (no-op in Phase 1).
- Playbooks page fetches via `apiClient.getPlaybooks()` and renders the card list.

## Task 21: Approvals Page | Phase: 1 | Files: ["apps/web/app/(dashboard)/approvals/page.tsx", "apps/web/components/approvals/ApprovalItem.tsx"] | Depends on: Task 4, Task 10
- `ApprovalItem` renders the pending action description, risk level badge, and Approve/Reject buttons (fire mock callbacks in Phase 1).
- Approvals page fetches via `apiClient.getApprovals()` and renders the list.

## Task 22: Log Stream Components | Phase: 1 | Files: ["apps/web/components/logs/LogEntry.tsx", "apps/web/components/logs/LogStream.tsx"] | Depends on: Task 2
- `LogEntry` renders timestamp, level badge (info/warn/error), agent name, and message.
- `LogStream` accepts `entries: LogEntry[]`, renders them in reverse-chronological order, and auto-scrolls to the latest entry using `useEffect` + a ref.

## Task 23: Logs Page | Phase: 1 | Files: ["apps/web/app/(dashboard)/logs/page.tsx"] | Depends on: Task 4, Task 22
- Fetches log entries via `apiClient.getLogs()`.
- Passes entries to `LogStream`.
- Provides level-filter buttons (All, Info, Warn, Error) with client-side filtering.

## Task 24: API Route Handlers | Phase: 1 | Files: ["apps/web/app/api/run/route.ts", "apps/web/app/api/status/[id]/route.ts"] | Depends on: Task 4, Task 5
- `POST /api/run` validates the request body, checks auth session via Supabase, and forwards the payload to `NEXT_PUBLIC_API_URL/run` (or returns a mock `task_id` when the env var is absent).
- `GET /api/status/[id]` forwards to FastAPI or returns mock status data.
- Both routes return typed JSON matching `ApiResponse<T>` from `types.ts`.

## Task 25: Realtime Integration | Phase: 2 | Files: ["apps/web/lib/realtime.ts"] | Depends on: Task 5, Task 24
- Implement `subscribeToAgentUpdates(callback)` and `subscribeToTaskUpdates(taskId, callback)` using Supabase Realtime channels.
- Export `unsubscribe()` cleanup functions for use in `useEffect` return values.
- Update `AgentGrid` and `ResponsePanel` to call these hooks so UI reflects live state without polling.

## Task 26: FastAPI Orchestration Engine | Phase: 2 | Files: ["apps/api/main.py", "apps/api/orchestrator.py", "apps/api/models.py"] | Depends on: Task 24
- `models.py`: Pydantic models mirroring `types.ts` — `Task`, `Agent`, `MemoryEntry`, etc.
- `orchestrator.py`: `Orchestrator` class with `decompose()`, `route()`, `retry()`, and `finalize()` methods; manages `task_id` lifecycle and writes status updates to Supabase.
- `main.py`: FastAPI app wiring `POST /run` and `GET /status/{id}` to the orchestrator; uses `BackgroundTasks` for async execution.

## Task 27: Agent Workers and Tool Layer | Phase: 2 | Files: ["apps/api/agents/base.py", "apps/api/agents/chief.py", "apps/api/agents/knowledge.py", "apps/api/agents/memory_writer.py", "apps/api/agents/critic.py", "apps/api/tools/search.py", "apps/api/tools/code_exec.py"] | Depends on: Task 26
- `base.py`: `BaseAgent` abstract class with `role`, `tools`, `memory`, and `execute(task) -> Result` contract.
- `chief.py`: `ChiefAgent` routes tasks through Planner → Specialist → Critic pipeline.
- `knowledge.py` / `memory_writer.py`: Supabase pgvector read/write for semantic retrieval and learning storage.
- `critic.py`: Reviews agent output and emits pass/fail with reasoning.
- `tools/search.py`: Serper API wrapper. `tools/code_exec.py`: sandboxed Python `subprocess` runner.

## Task 28: Deployment and Documentation | Phase: 2 | Files: ["docker-compose.yml", "apps/api/Dockerfile", "docs/readme.md", "docs/deploy.md"] | Depends on: Task 25, Task 27
- `docker-compose.yml`: Composes `web` (Next.js), `api` (FastAPI), and `redis` services for local development.
- `apps/api/Dockerfile`: Multi-stage Python 3.12 image optimised for Railway deployment.
- `docs/readme.md`: System overview, architecture diagram reference, and quickstart.
- `docs/deploy.md`: Step-by-step Vercel (web) + Railway (api) + Supabase (db/auth/realtime) production deployment guide including all required environment variables.

---
*Auto-updated as tasks complete. Do not edit manually.*