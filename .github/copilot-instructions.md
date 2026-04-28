# Copilot Instructions — ismael-agent-world

## Project
Private animated multi-agent AI command center. Universal task routing, dynamic agents, memory, playbooks, approvals, and execution logs.

## Owner
Solo founder (Ismael). Zero manual intervention. Every feature must be autonomous, low-touch, and scalable.

## Stack
Next.js App Router | TypeScript | Supabase | Tailwind CSS | Vercel | Lemon Squeezy

## Rules
- Always TypeScript, never `any`
- All agents are modular — each in its own file/module
- Memory layer via Supabase (pgvector preferred)
- Playbooks = reusable JSON task templates
- Approvals = async human-in-the-loop checkpoints before destructive actions
- Execution logs = append-only Supabase table
- Animations: Framer Motion only
- Payments: Lemon Squeezy (reuse shared payments package)
- Auth: Supabase Auth
- All secrets via environment variables, never hardcoded

## Agent Architecture
- Router Agent: classifies incoming tasks → routes to specialist agent
- Each specialist agent: input schema, output schema, Supabase memory read/write
- Playbook engine: loads JSON playbook → executes steps sequentially with checkpoint support
- Approval gate: pauses execution, notifies operator, resumes on confirm

## Code style
- Components: default export, PascalCase
- Utilities: named export, camelCase
- Database: snake_case columns
- API routes: /api/agents/[agentId], /api/tasks, /api/playbooks, /api/logs
