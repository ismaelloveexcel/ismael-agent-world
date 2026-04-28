# BLUEPRINT — Ismael Agent World

## One-line definition
A private animated multi-agent command center where one Chief Agent receives any request, classifies it, retrieves memory, selects or creates a playbook, generates temporary specialist agents, produces structured outputs, logs every step, and saves reusable learning.

## What it is
A private AI orchestration dashboard. Designed to replace jumping between ChatGPT, Claude, Claude Code, Perplexity, GitHub agents, and browser agents — those become execution modules behind your own interface.

## What it is NOT
- Not a normal chatbot
- Not a basic admin dashboard
- Not a fully autonomous system in Phase 1 or 2
- Not limited to ARIE Finance, app creation, HR, or any single domain

## Core Philosophy
Universal first, specialized later.
- Known domain → use memory and matching playbook
- Unknown domain → classify, create temporary specialist agent, generate domain capsule
- Repeated domain → promote to permanent sub-agent (3+ times threshold)

## Stack
- Next.js 15 App Router
- TypeScript (strict, no `any`)
- Tailwind CSS
- shadcn/ui style components
- Framer Motion (animations only)
- Supabase Postgres + pgvector ready
- OpenAI API primary | Anthropic secondary | Grok tertiary

## Pages
- /command — Main command center, central orb input
- /agents — Agent cards/nodes with live state
- /projects — Project workspace overview
- /memory — Memory vault (domain capsules, preferences)
- /playbooks — Playbook library
- /approvals — Approval queue for risky actions
- /logs — Execution log stream

## Core Agents (9)
1. Chief Agent — main entry point, owns final response
2. Intent Router Agent — classifies request type and domain
3. Knowledge Agent — retrieves relevant memory/context
4. Playbook Agent — selects or creates workflow
5. Dynamic Agent Generator — creates temporary specialist agents
6. Builder Agent — produces structured outputs
7. Critic/QA Agent — reviews for weakness/missing steps
8. Memory Agent — saves reusable learning
9. Approval Agent — creates approval records for risky actions

## Agent States
idle | thinking | retrieving_memory | selecting_playbook | generating_agent | building_output | reviewing | waiting_approval | completed | failed

## Command Flow
User request → Chief Agent → Intent Router → Knowledge Agent → Playbook Agent → Dynamic Agent Generator → Builder Agent → Critic/QA Agent → Memory Agent → Approval Agent → Chief Agent final response → Execution Log

## Default Playbooks
Build App | Build Automation | Build Dashboard/Table | Research Topic | Audit GitHub Repo | Create Business Model | Create Content Engine | Create SOP | Compare Tools | Launch Product | Build Agent | Create Database Schema

## TypeScript Types
Agent | DynamicAgent | Project | Task | TaskPacket | AgentRun | Memory | Playbook | Approval | ExecutionLog | ToolRegistryItem

## Database Tables
agents | dynamic_agents | projects | tasks | task_packets | agent_runs | agent_messages | handoffs | memories | domain_capsules | playbooks | generated_playbooks | approvals | tool_registry | tool_permissions | execution_logs | model_providers

## UI Requirements
- Premium dark command-center design (NOT generic admin)
- Deep navy/slate backgrounds, teal/blue accents
- Animated neural/particle background on /command
- Central command orb — pulses when processing
- Agent cards with state-based glow/animation
- Animated handoff lines between agents
- Activity stream with animated new events
- Approval drawer slides in for risky actions
- Framer Motion for ALL animations tied to state

## Phase 1 — Animated Shell
Goal: Premium animated interface with mock data. All 7 pages working. Feels like a private AI world.
Success: No blank pages, no console errors, animations meaningful, premium UI.

## Phase 2 — Agent Logic
Goal: Full workflow simulation. Chief Agent processes requests end-to-end with all 9 agents.
Success: Any request gets classified, playbook selected/generated, specialist agent created, output produced, logged, memory saved, approval records for risky actions.

## Safety Rules
- Phase 1+2: No real external actions
- No GitHub push/PR execution
- No MCP execution
- No real deployment
- No file deletion
- Risky actions → approval records only

## Dynamic Temporary Agents
Created when request doesn't fit permanent agents.
Expiry: archive after project completion unless promoted.
Promotion: 3+ same-domain uses, dedicated memory/tools needed, or manual pin.

## Memory Types
user_preference | project_memory | domain_capsule | playbook_memory | decision_log | prompt_library | agent_learning | repo_memory

## Approval Triggers (Phase 2+)
edit_file | delete_file | push_to_github | create_pr | deploy | payment_change | send_external_message | call_sensitive_api | access_credentials

## End Vision
Enter the dashboard and see:
  Welcome back, Ismael.
  Chief Agent online. Memory Engine ready.
  9 core agents available. 3 projects active. 2 approvals pending.
Type anything → system infers intent → structured output → only asks missing questions.
