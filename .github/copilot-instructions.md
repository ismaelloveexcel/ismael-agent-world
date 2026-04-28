# Copilot Instructions — ismael-agent-world

## Project
Private animated multi-agent AI command center. Universal and domain-agnostic. Phase 1: animated dashboard shell only — no real external actions.

## Owner
Solo founder (Ismael). Zero manual intervention. Premium quality only.

## Stack
Next.js 15 App Router | TypeScript (strict) | Tailwind CSS | shadcn/ui components | Framer Motion | Supabase-ready | Lemon Squeezy

## Pages
/command | /agents | /projects | /memory | /playbooks | /approvals | /logs

## Agents (9 core, mock/seed data)
Chief Agent → Intent Router → Knowledge Agent → Playbook Agent → Dynamic Agent Generator → Builder Agent → Critic/QA Agent → Memory Agent → Approval Agent

## Agent States
idle | thinking | retrieving_memory | selecting_playbook | generating_agent | building_output | reviewing | waiting_approval | completed | failed

## Rules
- TypeScript strict mode, never `any`
- Animations via Framer Motion only, tied to agent state
- All data is mock/seed — no real external API calls in Phase 1
- Risky actions create approval records, never execute
- No TODO comments, no empty pages, no console errors
- Premium dark UI — NOT a generic admin dashboard
- Particle/neural animated background on /command
- Agent handoff lines animated between nodes

## TypeScript types (all required)
Agent | DynamicAgent | Project | Task | TaskPacket | AgentRun | Memory | Playbook | Approval | ExecutionLog | ToolRegistryItem

## File structure
- /agents/* — agent logic modules
- /components/agents/* — agent UI components
- /components/ui/* — shadcn-style primitives
- /lib/mock/* — all mock data
- /lib/types.ts — all TypeScript types
- /app/command | /agents | /projects | /memory | /playbooks | /approvals | /logs