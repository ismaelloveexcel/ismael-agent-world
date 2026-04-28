# Ismael Agent World

A private animated multi-agent AI command center built with Next.js 15.

## Tech Stack

- **Next.js 15** App Router
- **TypeScript** (strict)
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **lucide-react** for icons

## Pages

| Route | Description |
|-------|-------------|
| `/command` | Main command center with animated orb and agent pipeline |
| `/agents` | All 9 core agent cards with state indicators |
| `/projects` | Active/paused/completed project cards |
| `/memory` | Memory fragments with semantic tags |
| `/playbooks` | 12 workflow playbook templates |
| `/approvals` | Pending/resolved approval gate items |
| `/logs` | Agent execution log stream |

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Agent Pipeline

The system includes 9 core agents:

1. **Chief Agent** - Orchestrates all requests
2. **Intent Router** - Classifies and routes tasks
3. **Knowledge Agent** - Retrieves context from memory
4. **Playbook Agent** - Selects workflow templates
5. **Dynamic Agent Generator** - Creates specialist agents
6. **Builder Agent** - Executes task output generation
7. **Critic / QA Agent** - Reviews and validates output
8. **Memory Agent** - Archives results and context
9. **Approval Agent** - Gates risky actions for human review
