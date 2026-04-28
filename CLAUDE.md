# ismael-agent-world — Repo Context

## What this is
Private animated multi-agent AI command center. Universal task routing, dynamic agents, memory system, playbooks, human-in-the-loop approvals, and execution logs.

## Stack
Next.js 14 App Router | TypeScript | Supabase (+ pgvector) | Tailwind CSS | Framer Motion | Vercel | Lemon Squeezy

## Key modules
- `/agents` — individual agent implementations (router, writer, researcher, etc.)
- `/playbooks` — JSON task templates
- `/lib/memory` — Supabase memory read/write
- `/lib/logs` — append-only execution log
- `/components` — animated UI components

## Secrets (check Notion API Vault first)
- ANTHROPIC_API_KEY
- OPENAI_API_KEY
- SUPABASE_URL + SUPABASE_ANON_KEY + SUPABASE_SERVICE_KEY
- LEMON_SQUEEZY_API_KEY

## Rules
- Zero manual intervention — automate everything
- All agent inputs/outputs are typed (Zod schemas)
- Memory is persistent via Supabase, never in-memory only
- Approvals are async — never block the main thread
