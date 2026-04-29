# Ismael Agent World — Master Build Plan
Generated: 2026-04-29T05:34:10.231232+00:00
By: GPT-4o → Claude (validation) → Grok (risk)

## Grok Risk Notes
As a senior engineer reviewing this build plan, here are the top 3 architectural risks for a solo non-technical developer, keeping it concise:

1. **Dependency Management Issues**: Without technical expertise, the developer may struggle with configuring and maintaining dependencies in `package.json` (Task 1). Incorrect versions or unresolved conflicts could break the project, delaying progress or causing runtime errors.

2. **TypeScript and Mock Data Misalignment**: Defining shared types and mock data (Task 2) requires understanding data structures and TypeScript. Errors or inconsistencies here could lead to UI or logic bugs, especially since downstream tasks like layout (Task 3) depend on this.

3. **Scalability of Layout and Theme Setup**: Building the layout and theme provider (Task 3) without architectural foresight might result in a rigid structure. A non-technical developer may not anticipate future needs (e.g., responsive design, accessibility), leading to costly refactoring later.

**Recommendation**: Simplify initial setup with templates (e.g., Next.js starters), use visual tools for mock data, and prioritize minimal, modular design to reduce complexity and rework. Consider outsourcing or pairing with a technical mentor for critical decisions.

---

## Summary
Total tasks: 23. Key changes: Added Task 3a (UI primitives/shadcn setup) before layout components; split Task 21 into deployment config and environment/docs; reordered so all shared components precede pages that consume them; verified no task exceeds 8 files; confirmed every phase-1 task is UI-deployable with mock data and every phase-2 task builds on a stable prior layer.

---

## Task 1: Setup Project Structure and Configuration | Phase: 1 | Files: tsconfig.json, package.json, next.config.ts, next-env.d.ts | Depends on: None [DONE]

1. Initialize the monorepo directory (`ismael-agent-world/apps/web`) and configure TypeScript with strict mode, path aliases (`@/*`), and Next.js plugin.
2. Add all required dependencies to `package.json`: Next.js 15, React 19, shadcn/ui, Framer Motion, Supabase JS client, Tailwind CSS, and dev tooling.
3. Create `next.config.ts` with App Router enabled and any required environment variable exposure.

---

## Task 2: Configure Tailwind, Global Styles, and shadcn/ui Primitives | Phase: 1 | Files: tailwind.config.ts, app/globals.css, components/ui/button.tsx, components/ui/card.tsx, components/ui/badge.tsx | Depends on: Task 1 [DONE]

1. Configure Tailwind CSS with the dark-mode `class` strategy, custom color tokens (background, foreground, accent), and the shadcn/ui content paths.
2. Write `globals.css` with CSS variable definitions for the dark theme and base resets.
3. Scaffold the three most-used shadcn/ui primitives (`Button`, `Card`, `Badge`) so all subsequent components can import them without circular dependencies.

---

## Task 3: Define Shared TypeScript Types | Phase: 1 | Files: lib/types.ts | Depends on: Task 1 [DONE]

1. Define all domain types used across UI and API boundary: `Agent`, `AgentStatus`, `Task`, `TaskStatus`, `MemoryEntry`, `Playbook`, `ApprovalItem`, `LogEntry`, `Project`, `CommandRequest`, `CommandResponse`.
2. Export every type from a single barrel so imports stay clean throughout the codebase.

---

## Task 4: Create Mock Data and Utility Helpers | Phase: 1 | Files: lib/mockData.ts, lib/utils.ts | Depends on: Task 3 [DONE]

1. Populate `mockData.ts` with realistic seed arrays for each domain type defined in `lib/types.ts` (agents, tasks, memory entries, playbooks, approvals, logs, projects).
2. Implement `lib/utils.ts` with the `cn()` class-merge helper (clsx + tailwind-merge) and any shared date/status formatting utilities consumed by components.

---

## Task 5: Build Root Layout and Theme Provider | Phase: 1 | Files: app/layout.tsx, components/layout/ThemeProvider.tsx | Depends on: Task 2, Task 4

1. Create `ThemeProvider.tsx` wrapping `next-themes` to enforce the dark theme and expose a toggle hook.
2. Build `app/layout.tsx` as the root server component: apply global font, mount `ThemeProvider`, render the `{children}` slot, and add the Supabase session hydration placeholder (static for now).

---

## Task 6: Implement Sidebar and Header Components | Phase: 1 | Files: components/layout/Sidebar.tsx, components/layout/Header.tsx | Depends on: Task 5

1. Design `Sidebar.tsx` with navigation links to all seven pages (`/command`, `/agents`, `/projects`, `/memory`, `/logs`, `/playbooks`, `/approvals`), active-route highlighting via `usePathname`, and a collapsed/expanded state using Framer Motion.
2. Create `Header.tsx` displaying the current page title, a notification bell badge (mock count), and a user avatar placeholder; wire both into the root layout.

---

## Task 7: Configure Supabase Client | Phase: 1 | Files: lib/supabase.ts | Depends on: Task 3

1. Initialize the Supabase browser client using `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` environment variables.
2. Export typed helper functions: `subscribeToAgentStatus(callback)`, `subscribeToTaskLogs(taskId, callback)`, and `unsubscribe(channel)` — all using Supabase Realtime channels so pages can subscribe without coupling to raw Supabase internals.

---

## Task 8: Develop Command Page and CommandInput Component | Phase: 1 | Files: app/command/page.tsx, components/command/CommandInput.tsx, components/command/OrbAnimation.tsx | Depends on: Task 6, Task 7

1. Build `OrbAnimation.tsx` as a Framer Motion animated orb that pulses when `isProcessing` is true and idles otherwise.
2. Implement `CommandInput.tsx` with a textarea, submit button, and keyboard shortcut (`Cmd+Enter`); on submit it calls the `/api/run` route (stubbed) and emits the task ID upward.
3. Compose `app/command/page.tsx`: center the orb above the input, show a live task-status line beneath it using mock data, and subscribe to Supabase agent-status channel (noop until Phase 2 backend is live).

---

## Task 9: Build Agent Page and AgentGrid Component | Phase: 1 | Files: app/agents/page.tsx, components/agents/AgentGrid.tsx, components/agents/AgentCard.tsx | Depends on: Task 6, Task 7

1. Create `AgentCard.tsx` rendering one agent's name, role, current status badge, last-active timestamp, and a subtle Framer Motion glow for `running` status.
2. Build `AgentGrid.tsx` accepting an `agents` array prop and rendering a responsive CSS grid of `AgentCard` elements.
3. Compose `app/agents/page.tsx`: seed from `mockData`, subscribe to the Supabase `agent_status` channel to merge live updates, and render `AgentGrid`.

---

## Task 10: Create Projects Page and Workspace Component | Phase: 1 | Files: app/projects/page.tsx, components/projects/Workspace.tsx, components/projects/ProjectCard.tsx | Depends on: Task 6, Task 4

1. Build `ProjectCard.tsx` showing project name, description, progress bar, and task count.
2. Implement `Workspace.tsx` with a selected-project detail panel (tasks list, status timeline) and an empty-state illustration.
3. Compose `app/projects/page.tsx`: list projects from mock data in a sidebar, render `Workspace` for the selected project, handle selection state with `useState`.

---

## Task 11: Implement Memory Page and MemoryCard Component | Phase: 1 | Files: app/memory/page.tsx, components/memory/MemoryCard.tsx, components/memory/MemorySearch.tsx | Depends on: Task 6, Task 4

1. Build `MemoryCard.tsx` displaying a memory entry's content snippet, source agent, timestamp, relevance score, and type tag.
2. Create `MemorySearch.tsx` with a debounced search input that filters the displayed entries client-side (semantic search wired in Phase 2).
3. Compose `app/memory/page.tsx`: render `MemorySearch` at the top, then a scrollable list of `MemoryCard` components seeded from mock data.

---

## Task 12: Create Logs Page and LogStream Component | Phase: 1 | Files: app/logs/page.tsx, components/logs/LogStream.tsx, components/logs/LogEntry.tsx | Depends on: Task 6, Task 7

1. Build `LogEntry.tsx` rendering a single log line with timestamp, level chip (INFO/WARN/ERROR), agent name, and message text.
2. Implement `LogStream.tsx` as a virtualized (or windowed) scrollable container that auto-scrolls to the bottom on new entries and accepts `entries` + `isLive` props.
3. Compose `app/logs/page.tsx`: mount `LogStream` with mock entries, subscribe to the Supabase `task_logs` channel to append real entries when available, and add a filter bar for log level.

---

## Task 13: Construct Playbooks Page and PlaybookLibrary Component | Phase: 1 | Files: app/playbooks/page.tsx, components/playbooks/PlaybookLibrary.tsx, components/playbooks/PlaybookCard.tsx | Depends on: Task 6, Task 4

1. Build `PlaybookCard.tsx` showing playbook name, trigger conditions, last-used date, success rate badge, and an expand chevron.
2. Implement `PlaybookLibrary.tsx` as a searchable, grouped list of `PlaybookCard` components with category tabs.
3. Compose `app/playbooks/page.tsx` seeded from mock playbook data; wire the "Run" button to call `/api/run` (stubbed).

---

## Task 14: Design Approvals Page and ApprovalQueue Component | Phase: 1 | Files: app/approvals/page.tsx, components/approvals/ApprovalQueue.tsx, components/approvals/ApprovalItem.tsx | Depends on: Task 6, Task 7

1. Build `ApprovalItem.tsx` with an approval card showing task description, risk level, requesting agent, and Approve/Reject action buttons.
2. Implement `ApprovalQueue.tsx` that groups items by priority and animates items out (Framer Motion layout) when approved or rejected.
3. Compose `app/approvals/page.tsx`: render `ApprovalQueue` with mock data; subscribe to Supabase `approvals` channel so new approval requests appear in real time.

---

## Task 15: Implement Root Redirect and 404 | Phase: 1 | Files: app/page.tsx, app/not-found.tsx | Depends on: Task 5

1. Create `app/page.tsx` as a server component that immediately redirects to `/command` using Next.js `redirect()`.
2. Create `app/not-found.tsx` with a minimal dark-themed 404 message and a back-to-command link so deep-link errors degrade gracefully.

---

## Task 16: Set Up API Gateway Route Handlers | Phase: 2 | Files: app/api/run/route.ts, app/api/status/[id]/route.ts, app/api/approve/[id]/route.ts | Depends on: Task 15

1. Implement `POST /api/run`: validate the request body against `CommandRequest`, forward the payload to the FastAPI engine via `fetch`, return the `task_id` and initial status as `CommandResponse`.
2. Implement `GET /api/status/[id]`: proxy the status request to FastAPI and stream the JSON response back; include error handling for 404 and 500.
3. Implement `POST /api/approve/[id]`: send an approval decision to FastAPI and return the updated task status.

---

## Task 17: Develop FastAPI Main Application | Phase: 2 | Files: apps/api/main.py, apps/api/config.py, apps/api/requirements.txt | Depends on: Task 16

1. Bootstrap the FastAPI app in `main.py` with CORS middleware (allowing the Vercel origin), lifespan startup/shutdown hooks, and route mounts for `/run`, `/status/{id}`, and `/approve/{id}`.
2. Centralize all environment variables (Supabase URL/key, Serper API key, Redis URL) in `config.py` using `pydantic-settings`.
3. Pin all Python dependencies in `requirements.txt` including `fastapi`, `uvicorn`, `supabase`, `openai`, `httpx`, `pydantic-settings`.

---

## Task 18: Implement Orchestrator for Task Lifecycle | Phase: 2 | Files: apps/api/orchestrator.py | Depends on: Task 17

1. Create `Orchestrator` class with `submit(task)` → assigns `task_id`, persists initial status to Supabase, enqueues via `BackgroundTasks`.
2. Implement `execute_pipeline(task_id)`: decompose the request via `ChiefAgent`, route to specialists, collect results, run `CriticAgent` review, write to memory, and update final status in Supabase.
3. Add retry logic (max 3 attempts with exponential backoff) and a `cancel(task_id)` method that sets status to `cancelled` in Supabase.

---

## Task 19: Define BaseAgent and Implement ChiefAgent and IntentRouterAgent | Phase: 2 | Files: apps/api/agents/base.py, apps/api/agents/chief.py, apps/api/agents/intent_router.py | Depends on: Task 18

1. Define `BaseAgent` abstract class with fields `role`, `tools`, `memory_client`; enforce the `async execute(input: AgentInput) -> AgentOutput` contract; add shared logging and error-wrapping.
2. Implement `ChiefAgent.execute()`: use the LLM to decompose the user request into an ordered list of sub-tasks with assigned agent types.
3. Implement `IntentRouterAgent.execute()`: classify each sub-task into a routing label (`knowledge`, `builder`, `playbook`, `approval_needed`) using a prompt with few-shot examples.

---

## Task 20: Build Specialist Agents | Phase: 2 | Files: apps/api/agents/knowledge.py, apps/api/agents/builder.py, apps/api/agents/playbook.py, apps/api/agents/critic.py, apps/api/agents/memory_writer.py, apps/api/agents/approval.py | Depends on: Task 19

1. `KnowledgeAgent`: run Serper web search + Supabase pgvector semantic retrieval; return ranked evidence blocks.
2. `BuilderAgent`: generate structured output (code, document, plan) from evidence + task spec; supports streaming output via Supabase Realtime.
3. `PlaybookAgent`: match the current task against stored playbooks; either execute a known playbook or flag for new-playbook creation.
4. `CriticAgent`: score builder output against task requirements; return pass/fail with revision notes; trigger a retry loop if score < threshold.
5. `MemoryWriterAgent`: extract key learnings from the completed task, embed them, and upsert into `memory_entries` table with metadata.
6. `ApprovalAgent`: evaluate risk level; if above threshold, insert an approval request into Supabase and pause the pipeline until the UI resolves it.

---

## Task 21: Implement Tool Layer | Phase: 2 | Files: apps/api/tools/search.py, apps/api/tools/code_exec.py, apps/api/tools/file_ops.py, apps/api/tools/http_caller.py | Depends on: Task 19

1. `search.py`: wrap Serper API with retry, result normalization, and a 10-result cap.
2. `code_exec.py`: run Python code in a subprocess sandbox with a 30-second timeout and stdout/stderr capture; reject shell injection patterns.
3. `file_ops.py`: scoped read/write/list helpers constrained to a `/workspace/{task_id}/` directory; raise on path traversal attempts.
4. `http_caller.py`: generic authenticated HTTP client with configurable headers, timeout, and response size limit.

---

## Task 22: Set Up Deployment Configuration | Phase: 2 | Files: Dockerfile, docker-compose.yml, vercel.json | Depends on: Task 17

1. Write `Dockerfile` for the FastAPI app: Python 3.12 slim base, install dependencies, run `uvicorn` on `PORT`.
2. Write `docker-compose.yml` for local dev: `api` service (Dockerfile), `web` service (Node 20), and a `redis` service; bind correct ports and share a `.env` file.
3. Create `vercel.json` setting the Next.js framework preset, environment variable passthrough for `API_URL`, and headers for the API proxy routes.

---

## Task 23: Environment Setup, README, and Integration Smoke Test |

---
*Auto-updated as tasks complete. Do not edit manually.*