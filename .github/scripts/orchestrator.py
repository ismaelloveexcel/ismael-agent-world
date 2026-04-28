#!/usr/bin/env python3
"""
Ismael Agent World — Autonomous Orchestrator v2
Flow:
  1. Read blueprint + codebase
  2. If no master plan → GPT-4o plans → Claude validates → save BUILD_PLAN.md
  3. Guard: if any agent PR is still open → wait (gatekeeper must merge it first)
  4. Pick next pending task from plan
  5. GPT-4o reviews approach → Claude writes code → GPT-4o complexity check
  6. If complexity > 7/10 → Claude simplifies
  7. Push branch + open PR (gatekeeper reviews before merge)
  8. On merge → orchestrator re-triggers automatically (see orchestrator.yml)
  9. Repeat until all tasks complete
"""

import os, sys, json, re, time, requests
from datetime import datetime, timezone, date
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY", "")
GROK_API_KEY      = os.environ.get("GROK_API_KEY", "")
GH_PAT            = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
REPO_OWNER        = os.environ.get("REPO_OWNER", "ismaelloveexcel")
REPO_NAME         = os.environ.get("REPO_NAME", "ismael-agent-world")
FOCUS_INPUT       = os.environ.get("FOCUS_INPUT", "").strip()
PHASE_INPUT       = os.environ.get("PHASE_INPUT", "1").strip()

CLAUDE_MODEL  = "claude-sonnet-4-6"
OPENAI_MODEL  = "gpt-4o"
GROK_MODEL    = "grok-3-fast"

BUILD_PLAN_PATH = ".github/BUILD_PLAN.md"
STATE_PATH      = ".github/agent-state.json"
BLUEPRINT_PATH  = "BLUEPRINT.md"

MAX_FILES_PER_PR   = 8
MAX_LINES_PER_PR   = 400
COMPLEXITY_LIMIT   = 7   # out of 10 — above this, Claude simplifies before PR
MAX_LINES_PER_FILE = 200

GH_API        = "https://api.github.com"
ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
OPENAI_API    = "https://api.openai.com/v1/chat/completions"
GROK_API_URL  = "https://api.x.ai/v1/chat/completions"

IGNORE_DIRS = {".git","node_modules",".next","dist","build",".github"}
IGNORE_EXTS = {".jpg",".jpeg",".png",".gif",".ico",".lock",".map",".woff",".woff2",".ttf",".eot"}

# ── Model Clients ────────────────────────────────────────────────────────────

def call_claude(prompt: str, system: str, max_tokens: int = 8000) -> str:
    resp = requests.post(ANTHROPIC_API, headers={
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }, json={"model": CLAUDE_MODEL, "max_tokens": max_tokens, "system": system,
             "messages": [{"role": "user", "content": prompt}]}, timeout=120)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

def call_openai(prompt: str, system: str, max_tokens: int = 1000) -> str:
    if not OPENAI_API_KEY: return ""
    resp = requests.post(OPENAI_API, headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"
    }, json={"model": OPENAI_MODEL, "max_tokens": max_tokens,
             "messages": [{"role":"system","content":system},{"role":"user","content":prompt}]}, timeout=60)
    if resp.status_code != 200: return ""
    return resp.json()["choices"][0]["message"]["content"]

def call_grok(prompt: str, system: str, max_tokens: int = 800) -> str:
    if not GROK_API_KEY: return ""
    resp = requests.post(GROK_API_URL, headers={
        "Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"
    }, json={"model": GROK_MODEL, "max_tokens": max_tokens,
             "messages": [{"role":"system","content":system},{"role":"user","content":prompt}]}, timeout=60)
    if resp.status_code != 200: return ""
    return resp.json()["choices"][0]["message"]["content"]

# ── GitHub Helpers ───────────────────────────────────────────────────────────

def gh(method: str, path: str, **kwargs):
    headers = {"Authorization": f"token {GH_PAT}", "Accept": "application/vnd.github.v3+json"}
    return requests.request(method, f"{GH_API}/{path}", headers=headers, timeout=30, **kwargs)

def load_state() -> dict:
    if Path(STATE_PATH).exists():
        return json.loads(Path(STATE_PATH).read_text())
    return {"version":2,"phase":1,"completed_tasks":[],"open_prs":[],"last_run":None,
            "total_runs":0,"plan_created":False}

def read_blueprint() -> str:
    return Path(BLUEPRINT_PATH).read_text() if Path(BLUEPRINT_PATH).exists() else ""

def read_build_plan() -> str:
    return Path(BUILD_PLAN_PATH).read_text() if Path(BUILD_PLAN_PATH).exists() else ""

def scan_codebase() -> str:
    lines = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if any(f.endswith(e) for e in IGNORE_EXTS): continue
            rel = os.path.join(root, f).lstrip("./")
            try:
                content = Path(root,f).read_text(errors="ignore").splitlines()[:40]
                lines.append(f"### {rel}\n" + "\n".join(content))
            except: pass
    return "\n\n".join(lines[:30])

def get_open_prs() -> list:
    resp = gh("GET", f"repos/{REPO_OWNER}/{REPO_NAME}/pulls?state=open")
    return [{"number":p["number"],"title":p["title"],"branch":p["head"]["ref"],
             "created_at":p["created_at"]} for p in resp.json()]

def get_agent_open_prs(open_prs: list) -> list:
    """Return only agent-opened PRs (branch starts with agent/)."""
    return [p for p in open_prs if p.get("branch","").startswith("agent/")]

def check_all_tasks_done(plan: str, completed_tasks: list) -> bool:
    """Check if every task in the plan is in the completed list."""
    completed_names = {t.get("task","").lower() for t in completed_tasks}
    task_lines = [l for l in plan.splitlines() if l.startswith("## Task")]
    if not task_lines:
        return False
    matched = sum(1 for tl in task_lines
                  if any(cn in tl.lower() for cn in completed_names))
    return matched >= len(task_lines)

def get_branch_sha(branch="main") -> str:
    resp = gh("GET", f"repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{branch}")
    return resp.json()["object"]["sha"]

def create_branch(branch_name: str):
    sha = get_branch_sha("main")
    gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/git/refs",
       json={"ref": f"refs/heads/{branch_name}", "sha": sha})

def push_files_to_branch(branch: str, files: list, commit_msg: str):
    branch_sha = get_branch_sha(branch)
    commit_resp = gh("GET", f"repos/{REPO_OWNER}/{REPO_NAME}/git/commits/{branch_sha}")
    base_tree_sha = commit_resp.json()["tree"]["sha"]

    tree_items = []
    for f in files:
        blob = gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/git/blobs",
                  json={"content": f["content"], "encoding": "utf-8"})
        tree_items.append({"path":f["path"],"mode":"100644","type":"blob","sha":blob.json()["sha"]})

    tree = gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/git/trees",
              json={"base_tree":base_tree_sha,"tree":tree_items})
    commit = gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/git/commits",
                json={"message":commit_msg,"tree":tree.json()["sha"],"parents":[branch_sha]})
    gh("PATCH", f"repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{branch}",
       json={"sha":commit.json()["sha"]})

def push_to_main(files: list, commit_msg: str):
    push_files_to_branch("main", files, commit_msg)

def create_pr(branch: str, title: str, body: str) -> dict:
    pr = gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/pulls",
            json={"title":title,"body":body,"head":branch,"base":"main"}).json()
    if pr.get("number"):
        gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/issues/{pr['number']}/labels",
           json={"labels":["agent","ai-task"]})
    return pr

def parse_json(text: str) -> dict:
    m = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if m: return json.loads(m.group(1))
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m: return json.loads(m.group(0))
    raise ValueError("No JSON found")

# ── Step 1: Master Plan Creation ─────────────────────────────────────────────

def create_master_plan(blueprint: str, codebase: str) -> str:
    print("\n📋 No master plan found. Creating one...")

    # GPT-4o plans
    print("   GPT-4o: generating plan...")
    gpt_plan = call_openai(f"""
Blueprint:
{blueprint[:5000]}

Current codebase:
{codebase[:1500]}

Create a detailed build plan for Phase 1 and Phase 2.
Rules:
- Max 8 files per PR, max 400 lines total per PR
- Start with: tsconfig, package.json, types, mock data, layout
- Then: shared components, then individual pages
- Each task must be self-contained and deployable
- Solo non-technical user — keep everything simple, no over-engineering
- Format each task as: ## Task N: <name> | Phase: <1|2> | Files: <list> | Depends on: <task N>

Output 20-25 tasks covering Phase 1 fully and Phase 2 outline.
""", "You are a senior Next.js architect creating a build plan for a solo developer. Be specific and practical.", max_tokens=3000)

    # Claude validates
    print("   Claude: validating plan...")
    validated = call_claude(f"""
Review this build plan for Ismael Agent World.

Blueprint requirements:
{blueprint[:3000]}

Proposed plan:
{gpt_plan}

Validate and improve this plan:
1. Are the tasks in the right order (dependencies respected)?
2. Is anything too complex for a solo non-technical user?
3. Are any tasks too large for one PR (>8 files or >400 lines)?
4. Is anything missing from Phase 1 requirements?
5. Are shared components built before pages that use them?

Output the corrected, final plan in the same format. Add a ## Summary section at the top with total tasks and estimated PRs.
""",
    "You are a TypeScript/Next.js expert validating a build plan. Be thorough but practical.",
    max_tokens=4000)

    # Grok adds creative perspective
    grok_note = call_grok(
        f"Build plan summary:\n{gpt_plan[:800]}\n\nAny architectural risk or simplification that would make this more robust for a solo developer? 3 bullet points max.",
        "You are a pragmatic senior engineer reviewing a build plan.", max_tokens=300)

    plan_content = f"""# Ismael Agent World — Master Build Plan
Generated: {datetime.now(timezone.utc).isoformat()}
By: GPT-4o (planning) → Claude (validation) → Grok (risk review)

## Grok Risk Notes
{grok_note}

---

{validated}

---
*This plan is updated automatically as tasks complete. Do not edit manually.*
"""
    return plan_content

# ── Step 2: Task Selection ────────────────────────────────────────────────────

def pick_next_task(plan: str, completed_tasks: list, codebase: str, focus: str) -> dict:
    completed_names = [t.get("task","") for t in completed_tasks]
    completed_str   = "\n".join(f"- {n}" for n in completed_names) or "None yet"

    result = call_openai(f"""
Build plan:
{plan[:4000]}

Completed tasks:
{completed_str}

Current codebase files:
{codebase[:1000]}

User focus (if any): {focus or "none — auto-select"}
Phase to work on: {PHASE_INPUT}

Which task should be done next?
- Must not duplicate completed tasks
- Must have all dependencies already done
- Must be Phase {PHASE_INPUT} if possible
- If user specified focus, prioritize that area

Reply with JSON only:
```json
{{
  "task_number": 5,
  "task_name": "Task name from plan",
  "why_now": "One sentence reason",
  "files_to_create": ["list", "of", "file", "paths"],
  "depends_on_done": true
}}
```
""", "You are a project manager selecting the next development task. Be decisive.", max_tokens=600)

    try:
        return parse_json(result)
    except:
        return {"task_number": 0, "task_name": "Auto-selected", "why_now": "No plan found",
                "files_to_create": [], "depends_on_done": True}

# ── Step 3: Code Generation ──────────────────────────────────────────────────

def generate_code(blueprint: str, codebase: str, task: dict, plan: str) -> dict:
    code_system = """You are an expert TypeScript/Next.js engineer building Ismael Agent World.

STRICT RULES — failure on any of these blocks the PR:
- TypeScript strict mode. Zero `any`. Full explicit types everywhere.
- Next.js 15 App Router. No pages directory. No `getServerSideProps`.
- Tailwind CSS only — no inline styles, no CSS modules.
- Framer Motion for ALL animations. Animations must reflect agent state, not be decorative.
- shadcn/ui component patterns.
- Mock/seed data only in Phase 1 — no real API calls, no fetch() to external services.
- Premium dark UI: bg-slate-950 or bg-navy-950, teal/blue accents (#0abf9f, #3b82f6).
- NOT a generic admin dashboard. Must feel like a private AI command center.
- Max 200 lines per file. If larger, split into sub-components.
- No TODO comments. No placeholder text. No console.log in production code.
- All imports must be real and resolvable.
- Use `@/` path aliases throughout.
- Output ONLY valid JSON. No commentary outside the JSON block."""

    code_prompt = f"""
TASK: {task['task_name']}
WHY: {task['why_now']}
FILES TO CREATE: {task.get('files_to_create', [])}

BLUEPRINT (key sections):
{blueprint[:6000]}

CURRENT CODEBASE:
{codebase[:2500]}

BUILD PLAN CONTEXT:
{plan[:1000]}

Generate ALL files completely. No partial files. No TODOs.
Max {MAX_FILES_PER_PR} files, max {MAX_LINES_PER_FILE} lines each.
If a component would be >200 lines, split it into sub-components automatically.

```json
{{
  "task_name": "{task['task_name']}",
  "rationale": "Why this is built this way",
  "branch_name": "agent/ph{PHASE_INPUT}-task{task.get('task_number',0)}-<slug>",
  "pr_title": "[Agent Ph{PHASE_INPUT}] Task {task.get('task_number',0)}: {task['task_name']}",
  "commit_message": "feat: <specific message>",
  "files": [
    {{
      "path": "path/to/file.tsx",
      "content": "complete file content",
      "line_count": 0
    }}
  ],
  "complexity_notes": "What was kept simple on purpose",
  "next_suggested_task": "Task name that should come next"
}}
```
"""
    raw = call_claude(code_prompt, code_system, max_tokens=8000)
    return parse_json(raw)

# ── Step 4: Complexity Check ─────────────────────────────────────────────────

def check_complexity(files: list) -> tuple[int, str]:
    files_preview = "\n".join([f"### {f['path']}\n{f['content'][:300]}" for f in files[:5]])
    result = call_openai(f"""
Rate the complexity of this code for a solo non-technical user to maintain (1=very simple, 10=very complex).

Context: This is Ismael Agent World — a private AI command center. The owner is a non-technical solo founder.

Files:
{files_preview}

Consider:
- Are there too many abstractions?
- Is the state management clear?
- Can someone unfamiliar with the codebase understand what each file does?
- Are components focused and single-purpose?

Reply with JSON:
```json
{{
  "score": 6,
  "issues": ["issue 1", "issue 2"],
  "simplifications": ["simplification 1", "simplification 2"]
}}
```
""", "You are a code complexity reviewer focused on maintainability for solo developers.", max_tokens=500)
    try:
        data = parse_json(result)
        return data.get("score", 5), json.dumps(data)
    except:
        return 5, "{}"

def simplify_code(files: list, complexity_notes: str) -> list:
    print(f"   Complexity too high. Claude simplifying...")
    files_str = json.dumps([{"path": f["path"], "content": f["content"]} for f in files])

    result = call_claude(f"""
These files are too complex (score > {COMPLEXITY_LIMIT}/10) for a solo non-technical user.

Complexity issues: {complexity_notes}

Files:
{files_str[:6000]}

Simplify them:
- Remove unnecessary abstractions
- Flatten component hierarchy where possible
- Use simpler state patterns (useState over complex reducers)
- Keep each file under 200 lines
- Keep all functionality intact — just make it clearer

Output the simplified files in the same JSON format:
```json
{{"files": [{{"path": "...", "content": "..."}}]}}
```
""", "You are a senior engineer simplifying code for maintainability. Keep all features, reduce complexity.", max_tokens=8000)

    data = parse_json(result)
    return data.get("files", files)

# ── Step 5: QA Review ────────────────────────────────────────────────────────

def qa_review(files: list, task_name: str) -> str:
    files_preview = "\n\n".join([f"### {f['path']}\n{f['content'][:500]}" for f in files[:6]])
    return call_openai(f"""
QA review for: {task_name}

Check each file for:
1. TypeScript errors (missing types, implicit any, undefined variables)
2. Missing or wrong imports
3. Broken JSX (unclosed tags, invalid props)
4. Next.js 15 App Router violations (wrong use of 'use client', server components issues)
5. Framer Motion misuse (wrong prop names, missing variants)
6. Tailwind classes that don't exist

Reply: PASS or list specific issues with file name and line reference.
Max 6 bullets if issues found.

Files:
{files_preview}
""", "You are a strict TypeScript/Next.js code reviewer. Be specific and concise.", max_tokens=500)

# ── Main ──────────────────────────