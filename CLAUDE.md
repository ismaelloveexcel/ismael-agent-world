# ismael-agent-world — Repo Context

## What this is
Private animated multi-agent AI command center. Universal, domain-agnostic. NOT limited to any single domain — Arie Finance, app creation, HR etc are examples only.

## Stack
- Next.js 15 App Router
- TypeScript (strict, no `any`)
- Tailwind CSS
- shadcn/ui style components
- Framer Motion (animations only via Framer)
- Supabase-ready structure (pgvector for memory)
- Lemon Squeezy (payments)

## Pages
- /command — Central command input/orb, task submission
- /agents — Animated agent cards/nodes with state
- /projects — Project cards
- /memory — Memory cards (persistent context)
- /playbooks — Playbook cards
- /approvals — Approval drawer
- /logs — Execution log stream

## Core Agents (mock/seed)
1. Chief Agent
2. Intent Router Agent
3. Knowledge Agent
4. Playbook Agent
5. Dynamic Agent Generator
6. Builder Agent
7. Critic/QA Agent
8. Memory Agent
9. Approval Agent

## Agent States
idle | thinking | retrieving_memory | selecting_playbook | generating_agent | building_output | reviewing | waiting_approval | completed | failed

## Command Flow (simulated)
1. Chief Agent receives request
2. Classifies task
3. Selects or generates playbook
4. Generates specialist agent if needed
5. Animated agent handoff
6. Activity stream entry
7. Mock memory save
8. Mock log entry
9. Risky actions → approval record (no execution)

## Default Playbooks
Build App | Build Automation | Build Dashboard/Table | Research Topic | Audit GitHub Repo | Create Business Model | Create Content Engine | Create SOP | Compare Tools | Launch Product | Build Agent | Create Database Schema

## TypeScript Types Required
Agent | DynamicAgent | Project | Task | TaskPacket | AgentRun | Memory | Playbook | Approval | ExecutionLog | ToolRegistryItem

## UI Requirements
- Premium dark command-center design
- Animated neural/particle background
- Central command orb
- Animated agent handoff lines
- Activity stream
- Approval drawer
- Responsive

## Safety (app behaviour)
- No real external actions
- No push/deploy/delete/API calls
- Approval records only for risky actions

## Secrets
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- NEXT_PUBLIC_SUPABASE_URL
- NEXT_PUBLIC_SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY

## Code conventions
- Components: default export, PascalCase
- Utilities: named export, camelCase
- DB columns: snake_case
- No TODO comments
- No console errors in production
- No empty placeholder pages