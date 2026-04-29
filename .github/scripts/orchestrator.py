#!/usr/bin/env python3
"""
Ismael Agent World — Autonomous Orchestrator v3 (10/10)

Fixes over v2:
  - Retry logic on every AI call (3 attempts, exponential backoff)
  - JSON parse retries with corrective re-prompting
  - Better codebase context: 80 lines/file, 50 files, sorted by mtime
  - Task completion tracked by task_number (not brittle string matching)
  - BUILD_PLAN.md updated with [DONE] markers after each task
  - Crash recovery: any unhandled exception opens a GitHub issue
  - Repo setup: enables auto-merge setting on first run
  - Concurrency handled by workflow (cancel-in-progress: false)
  - State pushed via dedicated bot commit (no branch-protection conflict)

Flow:
  1. Ensure repo is ready (auto-merge enabled)
  2. Read blueprint + codebase (full context)
  3. If no master plan → GPT-4o plans → Claude validates → save BUILD_PLAN.md
  4. Guard: if any agent PR still open → exit (gatekeeper must merge first)
  5. Check if all tasks done → celebrate + exit
  6. Pick next pending task (by task number)
  7. Claude writes code (with retry + JSON validation)
  8. GPT-4o complexity check → Claude simplifies if >7/10
  9. GPT-4o QA review
  10. Push branch + open PR → gatekeeper auto-reviews + auto-merges
  11. Update state + mark task [DONE] in BUILD_PLAN.md
"""

import os, sys, json, re, time, traceback, requests
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
COMPLEXITY_LIMIT   = 7
MAX_LINES_PER_FILE = 200
MAX_RETRIES        = 3

GH_API        = "https://api.github.com"
ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
OPENAI_API    = "https://api.openai.com/v1/chat/completions"
GROK_API_URL  = "https://api.x.ai/v1/chat/completions"

IGNORE_DIRS = {".git","node_modules",".next","dist","build",".github"}
IGNORE_EXTS = {".jpg",".jpeg",".png",".gif",".ico",".lock",
               ".map",".woff",".woff2",".ttf",".eot",".svg"}

# ── Model Clients with Retry ─────────────────────────────────────────────────

def call_claude(prompt: str, system: str, max_tokens: int = 8000) -> str:
    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(ANTHROPIC_API, headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }, json={"model": CLAUDE_MODEL, "max_tokens": max_tokens,
                     "system": system,
                     "messages": [{"role": "user", "content": prompt}]},
               timeout=180)
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]
        except Exception as e:
            last_err = e
            if attempt < MAX_RETRIES - 1:
                wait = 10 * (attempt + 1)
                print(f"   Claude attempt {attempt+1} failed ({e}). Retrying in {wait}s...")
                time.sleep(wait)
    raise RuntimeError(f"Claude failed after {MAX_RETRIES} attempts: {last_err}")

def call_openai(prompt: str, system: str, max_tokens: int = 1500) -> str:
    if not OPENAI_API_KEY:
        return ""
    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(OPENAI_API, headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            }, json={"model": OPENAI_MODEL, "max_tokens": max_tokens,
                     "messages": [{"role":"system","content":system},
                                  {"role":"user","content":prompt}]},
               timeout=90)
            if resp.status_code == 429:
                time.sleep(30)
                continue
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(10 * (attempt + 1))
    print(f"   OpenAI failed after {MAX_RETRIES} attempts: {last_err}")
    return ""

def call_grok(prompt: str, system: str, max_tokens: int = 800) -> str:
    if not GROK_API_KEY:
        return ""
    try:
        resp = requests.post(GROK_API_URL, headers={
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json",
        }, json={"model": GROK_MODEL, "max_tokens": max_tokens,
                 "messages": [{"role":"system","content":system},
                              {"role":"user","content":prompt}]},
           timeout=60)
        if resp.status_code != 200:
            return ""
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"   Grok failed (non-fatal): {e}")
        return ""

# ── JSON Parsing with Retry ──────────────────────────────────────────────────

def parse_json(text: str) -> dict:
    """Extract and parse JSON from model output."""
    # Try ```json blocks first
    m = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    # Try raw JSON object
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    raise ValueError(f"No valid JSON found in response (first 200 chars): {text[:200]}")

def call_claude_json(prompt: str, system: str, max_tokens: int = 8000,
                     context: str = "") -> dict:
    """Call Claude expecting JSON output. Retries with correction on parse failure."""
    current_prompt = prompt
    for attempt in range(MAX_RETRIES):
        raw = call_claude(current_prompt, system, max_tokens)
        try:
            return parse_json(raw)
        except (ValueError, json.JSONDecodeError) as e:
            if attempt < MAX_RETRIES - 1:
                print(f"   JSON parse failed (attempt {attempt+1}): {e}")
                current_prompt = (
                    f"{prompt}\n\n"
                    f"IMPORTANT — your previous response could not be parsed as JSON. "
                    f"Error: {e}\n"
                    f"You MUST respond with ONLY a valid JSON object. "
                    f"No explanation, no markdown prose, no text outside the JSON block. "
                    f"Start your response with ```json"
                )
            else:
                raise RuntimeError(
                    f"Claude failed to produce valid JSON after {MAX_RETRIES} attempts. "
                    f"Context: {context}. Last error: {e}"
                )

def call_openai_json(prompt: str, system: str, max_tokens: int = 1000) -> dict:
    """Call OpenAI expecting JSON output. Retries with correction on parse failure."""
    current_prompt = prompt
    for attempt in range(MAX_RETRIES):
        raw = call_openai(current_prompt, system, max_tokens)
        if not raw:
            return {}
        try:
            return parse_json(raw)
        except (ValueError, json.JSONDecodeError) as e:
            if attempt < MAX_RETRIES - 1:
                current_prompt = (
                    f"{prompt}\n\n"
                    f"IMPORTANT — previous response was not valid JSON. "
                    f"Respond with ONLY a JSON object inside ```json ... ```"
                )
            else:
                print(f"   OpenAI JSON parse failed: {e}. Using empty dict.")
                return {}

# ── GitHub Helpers ───────────────────────────────────────────────────────────

def gh(method: str, path: str, **kwargs):
    headers = {
        "Authorization": f"token {GH_PAT}",
        "Accept": "application/vnd.github.v3+json",
    }
    return requests.request(
        method, f"{GH_API}/{path}", headers=headers, timeout=30, **kwargs
    )

def load_state() -> dict:
    p = Path(STATE_PATH)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            print("   ⚠️  State file corrupted. Starting fresh.")
    return {
        "version": 3,
        "phase": 1,
        "completed_tasks": [],
        "open_prs": [],
        "last_run": None,
        "total_runs": 0,
        "plan_created": False,
        "repo_ready": False,
    }

def save_state(state: dict):
    """Save state to file and push to repo."""
    content = json.dumps(state, indent=2)
    Path(STATE_PATH).write_text(content)
    try:
        push_to_main(
            [{"path": STATE_PATH, "content": content}],
            f"chore: orchestrator state run #{state.get('total_runs', 0)}"
        )
    except Exception as e:
        print(f"   ⚠️  State push failed (non-fatal): {e}")

def read_blueprint() -> str:
    p = Path(BLUEPRINT_PATH)
    return p.read_text() if p.exists() else ""

def read_build_plan() -> str:
    p = Path(BUILD_PLAN_PATH)
    return p.read_text() if p.exists() else ""

def scan_codebase() -> str:
    """
    Scan repo files for context. Reads up to 80 lines per file, up to 50 files.
    Sorts by modification time (most recent first) so Claude sees what was just built.
    """
    entries = []
    for root, dirs, files in os.walk("."):
        dirs[:] = sorted([d for d in dirs if d not in IGNORE_DIRS])
        for fname in files:
            if any(fname.endswith(e) for e in IGNORE_EXTS):
                continue
            full = Path(root, fname)
            rel  = str(full).lstrip("./")
            try:
                mtime   = full.stat().st_mtime
                content = full.read_text(errors="ignore")
                lines   = content.splitlines()
                total   = len(lines)
                preview = lines[:80]
                entries.append((mtime, rel, total, "\n".join(preview)))
            except Exception:
                pass

    # Sort newest first — most relevant context at the top
    entries.sort(key=lambda x: x[0], reverse=True)

    parts = []
    for _, rel, total, preview in entries[:50]:
        parts.append(f"### {rel} ({total} lines total)\n{preview}")

    return "\n\n".join(parts)

def get_open_prs() -> list:
    resp = gh("GET", f"repos/{REPO_OWNER}/{REPO_NAME}/pulls?state=open&per_page=50")
    if resp.status_code != 200:
        return []
    return [
        {
            "number":     p["number"],
            "title":      p["title"],
            "branch":     p["head"]["ref"],
            "created_at": p["created_at"],
            "node_id":    p.get("node_id", ""),
        }
        for p in resp.json()
    ]

def get_agent_open_prs(open_prs: list) -> list:
    return [p for p in open_prs if p.get("branch", "").startswith("agent/")]

def extract_task_numbers_from_plan(plan: str) -> set:
    """Parse task numbers from plan headings like '## Task 5: Name'"""
    numbers = set()
    for line in plan.splitlines():
        m = re.match(r"##\s*Task\s*(\d+)\b", line, re.IGNORECASE)
        if m:
            numbers.add(int(m.group(1)))
    return numbers

def check_all_tasks_done(plan: str, completed_tasks: list) -> bool:
    """Reliable completion check using task numbers, not string matching."""
    plan_task_numbers = extract_task_numbers_from_plan(plan)
    if not plan_task_numbers:
        return False
    completed_numbers = set()
    for t in completed_tasks:
        num = t.get("task_num")
        if num is not None:
            try:
                completed_numbers.add(int(num))
            except (TypeError, ValueError):
                pass
    done = plan_task_numbers.issubset(completed_numbers)
    if done:
        print(f"   All {len(plan_task_numbers)} tasks complete: {sorted(plan_task_numbers)}")
    else:
        remaining = plan_task_numbers - completed_numbers
        print(f"   Tasks remaining: {sorted(remaining)} of {sorted(plan_task_numbers)}")
    return done

def mark_task_done_in_plan(plan: str, task_number: int, task_name: str) -> str:
    """Adds [DONE] marker to the completed task line in BUILD_PLAN.md."""
    lines = plan.splitlines()
    updated = []
    for line in lines:
        m = re.match(rf"##\s*Task\s*{task_number}\b", line, re.IGNORECASE)
        if m and "[DONE]" not in line:
            line = f"{line} [DONE]"
        updated.append(line)
    return "\n".join(updated)

def get_branch_sha(branch: str = "main") -> str:
    resp = gh("GET", f"repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{branch}")
    resp.raise_for_status()
    return resp.json()["object"]["sha"]

def create_branch(branch_name: str):
    sha = get_branch_sha("main")
    resp = gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/git/refs",
              json={"ref": f"refs/heads/{branch_name}", "sha": sha})
    if resp.status_code not in (200, 201, 422):
        resp.raise_for_status()

def push_files_to_branch(branch: str, files: list, commit_msg: str):
    """Push multiple files atomically using the Trees API."""
    branch_sha  = get_branch_sha(branch)
    commit_resp = gh("GET", f"repos/{REPO_OWNER}/{REPO_NAME}/git/commits/{branch_sha}")
    commit_resp.raise_for_status()
    base_tree_sha = commit_resp.json()["tree"]["sha"]

    tree_items = []
    for f in files:
        blob = gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/git/blobs",
                  json={"content": f["content"], "encoding": "utf-8"})
        blob.raise_for_status()
        tree_items.append({
            "path": f["path"], "mode": "100644",
            "type": "blob", "sha": blob.json()["sha"],
        })

    tree = gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/git/trees",
              json={"base_tree": base_tree_sha, "tree": tree_items})
    tree.raise_for_status()

    commit = gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/git/commits",
                json={"message": commit_msg,
                      "tree": tree.json()["sha"],
                      "parents": [branch_sha]})
    commit.raise_for_status()

    update = gh("PATCH", f"repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{branch}",
                json={"sha": commit.json()["sha"]})
    update.raise_for_status()

def push_to_main(files: list, commit_msg: str):
    push_files_to_branch("main", files, commit_msg)

def create_pr(branch: str, title: str, body: str) -> dict:
    pr = gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/pulls",
            json={"title": title, "body": body, "head": branch, "base": "main"})
    pr.raise_for_status()
    data = pr.json()
    if data.get("number"):
        gh("POST",
           f"repos/{REPO_OWNER}/{REPO_NAME}/issues/{data['number']}/labels",
           json={"labels": ["agent", "ai-task"]})
    return data

def open_failure_issue(error: str, run_context: str):
    """Opens a GitHub issue when the orchestrator crashes, so nothing is silent."""
    try:
        body = (
            "## Orchestrator run failed\n\n"
            f"**Run context:** {run_context}\n\n"
            "## Error\n"
            f"```\n{error[:3000]}\n```\n\n"
            "## What to do\n"
            "1. Check the Actions run log for full stack trace\n"
            "2. Trigger orchestrator manually once the issue is resolved\n\n"
            "---\n*Auto-opened by orchestrator crash handler*"
        )
        gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/issues",
           json={
               "title": f"[Orchestrator] Run failed — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
               "body": body,
               "labels": ["bug", "agent"],
           })
        print("   ⚠️  Failure issue opened on GitHub.")
    except Exception as e:
        print(f"   ⚠️  Could not open failure issue: {e}")

# ── Repo Setup ───────────────────────────────────────────────────────────────

def ensure_repo_ready(state: dict) -> dict:
    """Enable auto-merge on the repo (required for gatekeeper to merge PRs)."""
    if state.get("repo_ready"):
        return state
    resp = gh("PATCH", f"repos/{REPO_OWNER}/{REPO_NAME}",
              json={"allow_auto_merge": True, "allow_squash_merge": True,
                    "delete_branch_on_merge": True})
    if resp.status_code == 200:
        print("   ✅ Repo settings: auto-merge enabled, branch cleanup enabled")
        state["repo_ready"] = True
    else:
        print(f"   ⚠️  Repo settings update failed ({resp.status_code}) — continuing")
    return state

# ── Step 1: Master Plan Creation ─────────────────────────────────────────────

def create_master_plan(blueprint: str, codebase: str) -> str:
    print("\n📋 Step 1: Creating master build plan...")

    print("   GPT-4o: generating plan...")
    gpt_plan = call_openai(f"""
Blueprint:
{blueprint[:5000]}

Current codebase:
{codebase[:2000]}

Create a detailed build plan for Phase 1 and Phase 2.
Rules:
- Max 8 files per PR, max 400 lines total per PR
- Start with: tsconfig, package.json, types, mock data, layout
- Then: shared components, then individual pages
- Each task must be self-contained and independently deployable
- Solo non-technical user — no over-engineering, no unnecessary abstractions
- Format EXACTLY: ## Task N: <name> | Phase: <1|2> | Files: <list> | Depends on: Task N

Output 20-25 tasks. Number them sequentially starting from 1.
""", "You are a senior Next.js architect. Be specific. Use the exact format requested.",
        max_tokens=3500)

    print("   Claude: validating + improving plan...")
    validated = call_claude(f"""
Review this build plan for Ismael Agent World.

Blueprint:
{blueprint[:3000]}

Proposed plan:
{gpt_plan}

Validate and improve:
1. Tasks in correct dependency order?
2. Any task too large (>8 files or >400 total lines)?
3. Anything missing from Phase 1?
4. Shared components before pages that use them?
5. Every task independently deployable?

Output the corrected final plan in the EXACT same format.
Each heading MUST be: ## Task N: <name>
Include a ## Summary at the top with total task count.
""",
        "You are a TypeScript/Next.js expert. Keep the ## Task N: format exactly.",
        max_tokens=4000)

    grok_note = call_grok(
        f"Plan:\n{gpt_plan[:800]}\n\nTop 3 architectural risks for a solo non-technical developer?",
        "Senior engineer reviewing a build plan. Be concise.", max_tokens=300)

    return (
        f"# Ismael Agent World — Master Build Plan\n"
        f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
        f"By: GPT-4o → Claude (validation) → Grok (risk)\n\n"
        f"## Grok Risk Notes\n{grok_note}\n\n---\n\n"
        f"{validated}\n\n---\n"
        f"*Auto-updated as tasks complete. Do not edit manually.*\n"
    )

# ── Step 2: Task Selection ────────────────────────────────────────────────────

def pick_next_task(plan: str, completed_tasks: list, codebase: str, focus: str) -> dict:
    plan_numbers    = extract_task_numbers_from_plan(plan)
    completed_nums  = {int(t["task_num"]) for t in completed_tasks if t.get("task_num")}
    remaining_nums  = sorted(plan_numbers - completed_nums)
    completed_names = [t.get("task", "") for t in completed_tasks]
    completed_str   = "\n".join(f"- Task {t.get('task_num')}: {t.get('task')}" for t in completed_tasks) or "None yet"

    if not remaining_nums:
        return {"task_number": -1, "task_name": "All done", "why_now": "Complete",
                "files_to_create": [], "depends_on_done": True}

    data = call_openai_json(f"""
Build plan:
{plan[:4000]}

Completed tasks:
{completed_str}

Remaining task numbers: {remaining_nums}

Current codebase (newest files first):
{codebase[:1500]}

User focus: {focus or "none — auto-select by dependency order"}
Phase preference: {PHASE_INPUT}

Select the best next task from the remaining list.
Must have all its dependencies in the completed list.
If user specified focus, match it. Otherwise pick lowest-numbered valid task.

```json
{{
  "task_number": 5,
  "task_name": "Exact task name from plan",
  "why_now": "One sentence. Why this task, why now.",
  "files_to_create": ["src/path/to/file.tsx"],
  "depends_on_done": true
}}
```
""", "You are a project manager. Be decisive. Pick exactly one task.", max_tokens=600)

    return data if data.get("task_number") else {
        "task_number": remaining_nums[0] if remaining_nums else 0,
        "task_name": "Auto-selected",
        "why_now": "First remaining task",
        "files_to_create": [],
        "depends_on_done": True,
    }

# ── Step 3: Code Generation ──────────────────────────────────────────────────

def generate_code(blueprint: str, codebase: str, task: dict, plan: str) -> dict:
    task_num  = task.get("task_number", 0)
    task_name = task["task_name"]
    files_req = task.get("files_to_create", [])

    system = """You are an expert TypeScript/Next.js engineer building Ismael Agent World.

HARD RULES — any violation means the PR is rejected:
- TypeScript strict mode. Zero implicit `any`. Explicit types everywhere.
- Next.js 15 App Router only. No pages/. No getServerSideProps.
- Tailwind CSS only. No inline styles, no CSS modules.
- Framer Motion for all animations. Reflect agent state, not decorative.
- shadcn/ui component patterns.
- Phase 1: mock/seed data only. NO fetch() to external services.
- Dark UI: bg-slate-950 base, teal (#0abf9f) + blue (#3b82f6) accents.
- This is a private AI command center — NOT a generic admin dashboard.
- Max 200 lines per file. Split larger components automatically.
- No TODO comments. No placeholder text. No console.log.
- All imports must resolve. Use @/ path aliases.
- Output ONLY a valid JSON object. Zero text outside the JSON block."""

    prompt = f"""
TASK #{task_num}: {task_name}
FILES TO CREATE: {files_req}

BLUEPRINT:
{blueprint[:6000]}

CURRENT CODEBASE (newest first — import from these exact paths):
{codebase[:3000]}

BUILD PLAN CONTEXT:
{plan[:1500]}

Generate ALL files completely. No partial files.
If any file exceeds 200 lines, split into sub-components in the same PR.
Verify every import path against the CURRENT CODEBASE above.

```json
{{
  "task_name": "{task_name}",
  "rationale": "Why this is implemented this way",
  "branch_name": "agent/ph{PHASE_INPUT}-t{task_num}-{{}slug{{}}}",
  "pr_title": "[Agent Ph{PHASE_INPUT}] Task {task_num}: {task_name}",
  "commit_message": "feat: specific description of what was built",
  "files": [
    {{
      "path": "src/components/example.tsx",
      "content": "complete file content here",
      "line_count": 0
    }}
  ],
  "complexity_notes": "What was intentionally kept simple",
  "next_suggested_task": "Name of task that logically follows"
}}
```
"""
    return call_claude_json(prompt, system, max_tokens=8000, context=f"Task {task_num}: {task_name}")

# ── Step 4: Complexity Check ─────────────────────────────────────────────────

def check_complexity(files: list) -> tuple[int, str]:
    preview = "\n".join(
        f"### {f['path']}\n{f['content'][:400]}" for f in files[:6]
    )
    data = call_openai_json(f"""
Rate complexity for a solo non-technical founder to maintain (1=simple, 10=complex).

Files:
{preview}

Assess: too many abstractions? unclear state management? unfocused components?

```json
{{
  "score": 5,
  "issues": ["issue 1"],
  "simplifications": ["suggestion 1"]
}}
```
""", "Code complexity reviewer. Solo developer context.", max_tokens=500)
    score = data.get("score", 5)
    return int(score), json.dumps(data)

def simplify_code(files: list, complexity_notes: str) -> list:
    print("   Complexity too high — Claude simplifying...")
    files_json = json.dumps([{"path": f["path"], "content": f["content"]} for f in files])
    data = call_claude_json(f"""
These files scored >{COMPLEXITY_LIMIT}/10 complexity. Simplify them.

Issues: {complexity_notes}

Files:
{files_json[:7000]}

Rules:
- Remove unnecessary abstractions
- Flatten component trees where possible
- useState over complex reducers
- Keep each file <200 lines
- Keep ALL functionality intact

```json
{{"files": [{{"path": "...", "content": "..."}}]}}
```
""", "Senior engineer simplifying code. Keep features, reduce complexity.", max_tokens=8000)
    return data.get("files", files)

# ── Step 5: QA Review ────────────────────────────────────────────────────────

def qa_review(files: list, task_name: str) -> str:
    preview = "\n\n".join(
        f"### {f['path']}\n{f['content'][:600]}" for f in files[:6]
    )
    result = call_openai(f"""
QA review: {task_name}

Check for:
1. TypeScript errors (missing types, implicit any)
2. Missing or incorrect imports
3. Broken JSX (unclosed tags, invalid props)
4. Next.js 15 violations (wrong 'use client', server component issues)
5. Framer Motion misuse
6. Non-existent Tailwind classes
7. fetch() calls to external services (not allowed in Phase 1)
8. Any import path that doesn't exist in the codebase

Reply: PASS — then one sentence summary.
Or: ISSUES — then up to 6 bullet points with file + line reference.

Files:
{preview}
""", "Strict TypeScript/Next.js reviewer. Be specific.", max_tokens=600)
    return result or "PASS — QA skipped (OpenAI unavailable)"

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    run_context = f"Phase {PHASE_INPUT}, Focus: '{FOCUS_INPUT or 'auto'}'"
    print(f"=== Ismael Agent World — Orchestrator v3 ===")
    print(f"Models: Claude ({CLAUDE_MODEL}) | OpenAI ({OPENAI_MODEL}) | Grok ({GROK_MODEL})")
    print(f"Context: {run_context}")

    state     = load_state()
    blueprint = read_blueprint()
    codebase  = scan_codebase()
    open_prs  = get_open_prs()

    # ── Setup
    state = ensure_repo_ready(state)

    # ── Guard: 1 PR at a time
    agent_prs = get_agent_open_prs(open_prs)
    if agent_prs:
        info = ", ".join(f"#{p['number']} ({p['title'][:40]})" for p in agent_prs)
        print(f"\n⏸  Agent PR still open: {info}")
        print("   Waiting for gatekeeper to approve + merge before proceeding.")
        print("   Orchestrator auto-triggers once that PR is merged.")
        save_state(state)
        sys.exit(0)

    # ── Step 1: Master plan
    plan = read_build_plan()
    if not plan or not state.get("plan_created"):
        plan = create_master_plan(blueprint, codebase)
        Path(BUILD_PLAN_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(BUILD_PLAN_PATH).write_text(plan)
        push_to_main(
            [{"path": BUILD_PLAN_PATH, "content": plan}],
            "docs: create master build plan (GPT-4o + Claude + Grok)"
        )
        state["plan_created"] = True
        print("   ✅ Master plan saved to .github/BUILD_PLAN.md")
    else:
        print("✅ Master plan exists.")

    # ── Completion check
    if check_all_tasks_done(plan, state.get("completed_tasks", [])):
        print("\n🎉 ALL TASKS COMPLETE — Ismael Agent World is built!")
        print("   No more PRs will be opened. Phase 1 is done.")
        open_failure_issue.__doc__  # just to ensure it's importable
        gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/issues", json={
            "title": "🎉 Ismael Agent World — Phase 1 Build Complete",
            "body": (
                "The autonomous orchestrator has completed all tasks in the master build plan.\n\n"
                f"**Total runs:** {state.get('total_runs', 0)}\n"
                f"**Tasks completed:** {len(state.get('completed_tasks', []))}\n\n"
                "Review the codebase and deploy to Vercel to go live."
            ),
            "labels": ["agent"],
        })
        save_state(state)
        sys.exit(0)

    # ── Step 2: Pick next task
    print("\n🧠 Step 2: Selecting next task...")
    task = pick_next_task(plan, state.get("completed_tasks", []), codebase, FOCUS_INPUT)
    if task.get("task_number") == -1:
        print("   All tasks complete per state. Exiting.")
        sys.exit(0)
    print(f"   Task #{task.get('task_number')}: {task['task_name']}")
    print(f"   Why: {task['why_now']}")

    # ── Step 3: Generate code
    print(f"\n⚡ Step 3: Claude generating code...")
    plan_data = generate_code(blueprint, codebase, task, plan)
    files     = plan_data.get("files", [])
    if not files:
        raise RuntimeError(f"Claude returned no files for task #{task.get('task_number')}")

    print(f"   {len(files)} files generated:")
    total_lines = 0
    for f in files:
        lines = len(f["content"].splitlines())
        total_lines += lines
        print(f"   - {f['path']} ({lines} lines)")
    print(f"   Total: {total_lines} lines")

    if len(files) > MAX_FILES_PER_PR:
        print(f"   ⚠️  Trimming from {len(files)} to {MAX_FILES_PER_PR} files.")
        files = files[:MAX_FILES_PER_PR]

    # ── Step 4: Complexity check
    print("\n🔍 Step 4: Complexity check...")
    complexity_score, complexity_detail = check_complexity(files)
    print(f"   Score: {complexity_score}/10")
    if complexity_score > COMPLEXITY_LIMIT:
        print(f"   ⚠️  Too complex. Simplifying...")
        files = simplify_code(files, complexity_detail)

    # ── Step 5: QA review
    print("\n🔎 Step 5: QA review...")
    qa = qa_review(files, task["task_name"])
    print(f"   QA: {qa[:150]}")

    # ── Step 6: PR body
    print("\n📝 Step 6: Building PR description...")
    file_list = "\n".join(
        f"- `{f['path']}` ({len(f['content'].splitlines())} lines)" for f in files
    )
    pr_body = call_openai(f"""
Write a GitHub PR description.
Task #{task.get('task_number')}: {task['task_name']}
Why: {task['why_now']}
Complexity: {complexity_score}/10
QA: {qa}

Files:
{file_list}

Use these sections:
## What this PR does
## Blueprint alignment
## Files changed
## How to verify
## QA result

Concise. Solo project — no corporate review language.
""", "Writing a PR description. Clear and direct.", max_tokens=700)
    pr_body += (
        f"\n\n---\n"
        f"*Orchestrator run #{state.get('total_runs', 0)+1} · "
        f"Claude (code) + GPT-4o (QA/complexity) + Grok (risk) · "
        f"Gatekeeper will auto-merge after review*"
    )

    # ── Step 7: Push branch + open PR
    branch     = plan_data.get("branch_name", f"agent/ph{PHASE_INPUT}-t{task.get('task_number',0)}-auto")
    # sanitise branch name
    branch = re.sub(r"[^a-zA-Z0-9/_-]", "-", branch).rstrip("-")
    pr_title   = plan_data.get("pr_title", f"[Agent] Task {task.get('task_number',0)}: {task['task_name']}")
    commit_msg = plan_data.get("commit_message", f"feat: {task['task_name']}")

    print(f"\n🌿 Step 7: Branch {branch}...")
    create_branch(branch)
    time.sleep(1)

    print("📁 Pushing files...")
    push_files_to_branch(branch, files, commit_msg)

    print("🔀 Opening PR...")
    pr     = create_pr(branch, pr_title, pr_body)
    pr_num = pr.get("number", 0)
    pr_url = pr.get("html_url", "")
    print(f"   PR #{pr_num}: {pr_url}")

    # ── Step 8: Update state + plan
    completed_entry = {
        "task":       task["task_name"],
        "task_num":   task.get("task_number"),
        "branch":     branch,
        "pr":         pr_num,
        "pr_url":     pr_url,
        "date":       date.today().isoformat(),
        "files":      [f["path"] for f in files],
        "complexity": complexity_score,
        "qa":         qa[:150],
        "next":       plan_data.get("next_suggested_task", ""),
    }
    state["completed_tasks"].append(completed_entry)
    state["last_run"]   = datetime.now(timezone.utc).isoformat()
    state["total_runs"] = state.get("total_runs", 0) + 1
    state["open_prs"]   = get_open_prs()

    # Mark task done in plan
    updated_plan = mark_task_done_in_plan(plan, task.get("task_number", 0), task["task_name"])
    Path(BUILD_PLAN_PATH).write_text(updated_plan)

    # Push state + updated plan together
    push_to_main([
        {"path": STATE_PATH,      "content": json.dumps(state, indent=2)},
        {"path": BUILD_PLAN_PATH, "content": updated_plan},
    ], f"chore: mark Task {task.get('task_number')} done, run #{state['total_runs']}")

    print(f"\n🎯 Done. PR #{pr_num} → gatekeeper reviewing → auto-merges → next task triggers.")
    print(f"   Next: {plan_data.get('next_suggested_task', 'TBD')}")
    print(f"   PR:   {pr_url}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        tb = traceback.format_exc()
        print(f"\n💥 ORCHESTRATOR CRASH:\n{tb}")
        phase   = os.environ.get("PHASE_INPUT", "?")
        focus   = os.environ.get("FOCUS_INPUT", "auto")
        context = f"Phase {phase}, Focus '{focus}'"
        open_failure_issue(tb, context)
        sys.exit(1)
