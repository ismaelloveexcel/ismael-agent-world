#!/usr/bin/env python3
"""
Ismael Agent World — Autonomous Orchestrator
Multi-model: Claude (code), GPT-4o (planning), Grok (ideation/inspiration)
Auto-merges on CI pass. Zero manual intervention required.
"""

import os, sys, json, time, re, requests
from datetime import datetime, timezone
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

# Model routing — each model used for what it's best at:
# Grok      → GitHub inspiration scraping, creative ideation
# GPT-4o    → Task planning, PR description, QA review pass
# Claude    → Full TypeScript/Next.js code generation (primary engine)
CLAUDE_MODEL   = "claude-sonnet-4-6"
OPENAI_MODEL   = "gpt-4o"
GROK_MODEL     = "grok-3-fast"

STATE_PATH     = ".github/agent-state.json"
BLUEPRINT_PATH = "BLUEPRINT.md"
GH_API         = "https://api.github.com"
ANTHROPIC_API  = "https://api.anthropic.com/v1/messages"
OPENAI_API     = "https://api.openai.com/v1/chat/completions"
GROK_API       = "https://api.x.ai/v1/chat/completions"

IGNORE_DIRS = {".git", "node_modules", ".next", "dist", "build", ".github"}
IGNORE_EXTS = {".jpg",".jpeg",".png",".gif",".ico",".lock",".map",".woff",".woff2",".ttf",".eot"}

# ── Model Clients ────────────────────────────────────────────────────────────

def call_claude(prompt: str, system: str, max_tokens: int = 8000) -> str:
    """Claude Sonnet — primary code generation engine."""
    resp = requests.post(ANTHROPIC_API, headers={
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }, json={
        "model": CLAUDE_MODEL, "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }, timeout=120)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

def call_openai(prompt: str, system: str, model: str = None, max_tokens: int = 1500) -> str:
    """GPT-4o — planning, QA, PR descriptions."""
    if not OPENAI_API_KEY:
        return ""
    resp = requests.post(OPENAI_API, headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }, json={
        "model": model or OPENAI_MODEL, "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
    }, timeout=60)
    if resp.status_code != 200:
        return ""
    return resp.json()["choices"][0]["message"]["content"]

def call_grok(prompt: str, system: str, max_tokens: int = 1000) -> str:
    """Grok — creative ideation and GitHub inspiration analysis."""
    if not GROK_API_KEY:
        return ""
    resp = requests.post(GROK_API, headers={
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }, json={
        "model": GROK_MODEL, "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
    }, timeout=60)
    if resp.status_code != 200:
        return ""
    return resp.json()["choices"][0]["message"]["content"]

# ── GitHub Helpers ───────────────────────────────────────────────────────────

def gh_headers():
    return {"Authorization": f"token {GH_PAT}", "Accept": "application/vnd.github.v3+json"}

def load_state() -> dict:
    if Path(STATE_PATH).exists():
        return json.loads(Path(STATE_PATH).read_text())
    return {"version":1,"phase":1,"completed_tasks":[],"open_prs":[],"last_run":None,"total_runs":0}

def save_state_to_repo(state: dict):
    Path(STATE_PATH).write_text(json.dumps(state, indent=2))
    content = json.dumps(state, indent=2)
    push_files_to_branch("main",
        [{"path": STATE_PATH, "content": content}],
        f"chore: orchestrator state run #{state.get('total_runs',0)}")

def read_blueprint() -> str:
    return Path(BLUEPRINT_PATH).read_text() if Path(BLUEPRINT_PATH).exists() else ""

def scan_codebase() -> str:
    lines = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if any(f.endswith(e) for e in IGNORE_EXTS): continue
            rel = os.path.join(root, f).lstrip("./")
            try:
                content = Path(root, f).read_text(errors="ignore").splitlines()[:50]
                lines.append(f"### {rel}\n" + "\n".join(content))
            except: pass
    return "\n\n".join(lines[:35])

def get_open_prs() -> list:
    resp = requests.get(f"{GH_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls?state=open", headers=gh_headers())
    return [{"number": p["number"], "title": p["title"], "branch": p["head"]["ref"]}
            for p in resp.json()]

def search_github_inspiration(codebase_str: str) -> str:
    """Use Grok to ideate on architecture, plus GitHub search for patterns."""
    grok_ideation = ""
    if GROK_API_KEY:
        grok_ideation = call_grok(
            f"We are building a premium animated multi-agent AI command center in Next.js 15. "
            f"Current files: {codebase_str[:500]}. "
            f"What are the most impressive architectural patterns or UI tricks used in top open-source AI dashboards? "
            f"Give 3 specific ideas that would make this feel premium. Be concise.",
            "You are a creative senior engineer and product designer specializing in AI tooling UIs.",
            max_tokens=600
        )

    # GitHub API search
    resp = requests.get(f"{GH_API}/search/repositories", headers=gh_headers(),
        params={"q": "multi-agent nextjs dashboard framer-motion", "sort": "stars", "per_page": 3})
    gh_results = ""
    if resp.status_code == 200:
        items = resp.json().get("items", [])
        for r in items[:3]:
            gh_results += f"\n- {r['full_name']} ({r['stargazers_count']}★): {r.get('description','')}"

    return f"Grok ideation:\n{grok_ideation}\n\nGitHub similar projects:{gh_results}"

def create_branch(branch_name: str) -> str:
    resp = requests.get(f"{GH_API}/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/main", headers=gh_headers())
    sha = resp.json()["object"]["sha"]
    r = requests.post(f"{GH_API}/repos/{REPO_OWNER}/{REPO_NAME}/git/refs",
        headers=gh_headers(), json={"ref": f"refs/heads/{branch_name}", "sha": sha})
    if r.status_code not in [201, 422]:
        print(f"Branch create: {r.status_code} {r.text[:200]}")
    return sha

def push_files_to_branch(branch: str, files: list, commit_msg: str):
    resp = requests.get(f"{GH_API}/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{branch}", headers=gh_headers())
    if resp.status_code != 200: return
    branch_sha = resp.json()["object"]["sha"]

    commit_resp = requests.get(f"{GH_API}/repos/{REPO_OWNER}/{REPO_NAME}/git/commits/{branch_sha}", headers=gh_headers())
    base_tree_sha = commit_resp.json()["tree"]["sha"]

    tree_items = []
    for f in files:
        blob = requests.post(f"{GH_API}/repos/{REPO_OWNER}/{REPO_NAME}/git/blobs",
            headers=gh_headers(), json={"content": f["content"], "encoding": "utf-8"})
        tree_items.append({"path": f["path"], "mode": "100644", "type": "blob", "sha": blob.json()["sha"]})

    tree = requests.post(f"{GH_API}/repos/{REPO_OWNER}/{REPO_NAME}/git/trees",
        headers=gh_headers(), json={"base_tree": base_tree_sha, "tree": tree_items})
    new_tree_sha = tree.json()["sha"]

    commit = requests.post(f"{GH_API}/repos/{REPO_OWNER}/{REPO_NAME}/git/commits",
        headers=gh_headers(), json={"message": commit_msg, "tree": new_tree_sha, "parents": [branch_sha]})
    new_commit_sha = commit.json()["sha"]

    requests.patch(f"{GH_API}/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{branch}",
        headers=gh_headers(), json={"sha": new_commit_sha})

def create_pr_with_automerge(branch: str, title: str, body: str) -> dict:
    # Enable auto-merge on repo (requires admin)
    requests.patch(f"{GH_API}/repos/{REPO_OWNER}/{REPO_NAME}",
        headers=gh_headers(), json={"allow_auto_merge": True, "allow_squash_merge": True})

    # Create PR
    pr_resp = requests.post(f"{GH_API}/repos/{REPO_OWNER}/{REPO_NAME}/pulls",
        headers=gh_headers(), json={"title": title, "body": body, "head": branch, "base": "main"})
    pr = pr_resp.json()
    pr_num = pr.get("number", 0)

    if not pr_num:
        print(f"PR creation failed: {pr_resp.text[:300]}")
        return pr

    # Add labels
    requests.post(f"{GH_API}/repos/{REPO_OWNER}/{REPO_NAME}/issues/{pr_num}/labels",
        headers=gh_headers(), json={"labels": ["agent", "ai-task"]})

    # Enable auto-merge via GraphQL
    node_id = pr.get("node_id", "")
    if node_id:
        gql_query = """
        mutation EnableAutoMerge($pullRequestId: ID!) {
          enablePullRequestAutoMerge(input: {pullRequestId: $pullRequestId, mergeMethod: SQUASH}) {
            pullRequest { autoMergeRequest { enabledAt } }
          }
        }"""
        gql_resp = requests.post("https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {GH_PAT}", "Content-Type": "application/json"},
            json={"query": gql_query, "variables": {"pullRequestId": node_id}})
        if gql_resp.status_code == 200 and not gql_resp.json().get("errors"):
            print(f"   ✅ Auto-merge enabled on PR #{pr_num}")
        else:
            print(f"   ⚠️  Auto-merge not available (branch protection may need required checks). Manual merge needed.")

    return pr

def parse_json_response(text: str) -> dict:
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match: return json.loads(match.group(1))
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match: return json.loads(match.group(0))
    raise ValueError("No JSON in response")

# ── Main Pipeline ────────────────────────────────────────────────────────────

def main():
    print("=== Ismael Agent World — Orchestrator ===")
    print(f"Models: Claude ({CLAUDE_MODEL}) | OpenAI ({OPENAI_MODEL}) | Grok ({GROK_MODEL})")

    state       = load_state()
    blueprint   = read_blueprint()
    codebase    = scan_codebase()
    open_prs    = get_open_prs()

    if len(open_prs) >= 4:
        print(f"⏸  {len(open_prs)} PRs open. Pausing. Auto-merge should clear these via CI.")
        sys.exit(0)

    # ── Step 1: Grok ideation (creative spark) ────────────────────────────────
    print("\n🔮 Step 1: Grok — creative ideation + GitHub inspiration...")
    inspiration = search_github_inspiration(codebase)
    print(inspiration[:400])

    # ── Step 2: GPT-4o planning (what to build next) ──────────────────────────
    print("\n🧠 Step 2: GPT-4o — task planning...")
    completed_str = json.dumps(state.get("completed_tasks", [])[-5:], indent=2)  # last 5
    open_prs_str  = json.dumps(open_prs, indent=2)
    focus_str     = f"User focus: {FOCUS_INPUT}" if FOCUS_INPUT else ""

    planning_prompt = f"""
Blueprint summary (first 3000 chars):
{blueprint[:3000]}

Current codebase files:
{codebase[:2000]}

Completed tasks (last 5):
{completed_str}

Open PRs:
{open_prs_str}

{focus_str}

Phase: {PHASE_INPUT}

What is the single most important next task to build? Consider what's missing vs the blueprint.
Reply in 3 sentences: 1) what to build, 2) why it's most important now, 3) which files to create/edit.
"""
    planning_result = call_openai(planning_prompt,
        "You are a senior product engineer planning the next sprint task for an AI command center app.",
        max_tokens=500)
    if planning_result:
        print(f"   GPT-4o plan: {planning_result[:300]}")
    else:
        print("   GPT-4o unavailable — Claude will self-plan.")

    # ── Step 3: Claude code generation (primary engine) ───────────────────────
    print(f"\n⚡ Step 3: Claude {CLAUDE_MODEL} — code generation...")

    code_system = """You are an expert autonomous TypeScript/Next.js engineer building Ismael Agent World.
Rules:
- Generate complete, working, production-quality code. No TODOs, no placeholders.
- TypeScript strict mode. No `any`. Full type safety.
- Next.js 15 App Router patterns.
- Framer Motion for ALL animations — tied to agent state, not decorative.
- Mock/seed data only in Phase 1. No real API calls.
- shadcn/ui component patterns with Tailwind.
- Premium dark UI: deep navy/slate backgrounds, teal/blue accents, never generic admin look.
- Output ONLY valid JSON in the exact format requested. No commentary outside the JSON."""

    code_prompt = f"""
BLUEPRINT (full):
{blueprint[:10000]}

CURRENT CODEBASE:
{codebase[:3000]}

COMPLETED TASKS:
{completed_str}

GPT-4o PLANNING INPUT:
{planning_result or "Self-determine based on blueprint and codebase state."}

INSPIRATION:
{inspiration[:800]}

Build the next task. Generate ALL file contents completely.

Respond ONLY with this JSON:
```json
{{
  "task_name": "Short task name",
  "rationale": "Why this is the most important next step",
  "branch_name": "agent/ph{PHASE_INPUT}-<slug>",
  "pr_title": "[Agent Ph{PHASE_INPUT}] <title>",
  "commit_message": "feat: <message>",
  "files": [
    {{
      "path": "relative/path/file.ts",
      "content": "complete file content"
    }}
  ],
  "next_suggested_task": "What should come after this"
}}
```
"""
    raw = call_claude(code_prompt, code_system, max_tokens=8000)
    plan = parse_json_response(raw)

    branch    = plan["branch_name"]
    files     = plan["files"]
    task_name = plan["task_name"]

    print(f"\n✅ Task: {task_name}")
    print(f"   Branch: {branch} | Files: {len(files)}")
    for f in files:
        print(f"   - {f['path']} ({len(f['content'])} chars)")

    # ── Step 4: GPT-4o QA review (catch obvious issues) ───────────────────────
    print("\n🔍 Step 4: GPT-4o — QA review...")
    files_summary = "\n".join([f"### {f['path']}\n{f['content'][:400]}" for f in files])
    qa_result = call_openai(
        f"QA review these TypeScript/Next.js files for: type errors, missing imports, "
        f"broken JSX, undefined variables, animation correctness. "
        f"Reply with PASS or list specific issues (max 5 bullets).\n\n{files_summary[:3000]}",
        "You are a TypeScript/Next.js code reviewer. Be concise and specific.",
        max_tokens=400)
    print(f"   QA: {(qa_result or 'skipped')[:200]}")

    # ── Step 5: GPT-4o writes PR description ─────────────────────────────────
    print("\n📝 Step 5: GPT-4o — PR description...")
    pr_body = call_openai(
        f"Write a clear GitHub PR description for this change.\n"
        f"Task: {task_name}\nRationale: {plan['rationale']}\n"
        f"Files: {[f['path'] for f in files]}\nQA result: {qa_result or 'not run'}\n\n"
        f"Format: ## What | ## Why | ## Files | ## QA | ## Next",
        "You are a senior engineer writing a GitHub PR description. Be clear and direct.",
        max_tokens=500)
    if not pr_body:
        pr_body = f"## {task_name}\n\n{plan['rationale']}\n\nFiles: {[f['path'] for f in files]}"
    pr_body += "\n\n---\n*Auto-generated by Orchestrator (Claude + GPT-4o + Grok)*"

    # ── Step 6: Push + PR + Auto-merge ───────────────────────────────────────
    print(f"\n🌿 Creating branch {branch}...")
    create_branch(branch)
    time.sleep(1)

    print("📁 Pushing files...")
    push_files_to_branch(branch, files, plan["commit_message"])

    print("🔀 Opening PR with auto-merge...")
    pr = create_pr_with_automerge(branch, plan["pr_title"], pr_body)
    pr_url = pr.get("html_url", "unknown")
    pr_num = pr.get("number", 0)
    print(f"   PR #{pr_num}: {pr_url}")

    # ── Step 7: Update state ──────────────────────────────────────────────────
    state["completed_tasks"].append({
        "task": task_name,
        "branch": branch,
        "pr": pr_num,
        "pr_url": pr_url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "files": [f["path"] for f in files],
        "qa": (qa_result or "")[:200],
        "next_suggested": plan.get("next_suggested_task", ""),
    })
    state["last_run"]   = datetime.now(timezone.utc).isoformat()
    state["total_runs"] = state.get("total_runs", 0) + 1
    state["open_prs"]   = get_open_prs()

    save_state_to_repo(state)

    print(f"\n🎯 Done! Run #{state['total_runs']} complete.")
    print(f"   PR #{pr_num} → auto-merges when CI passes.")
    print(f"   Next: {plan.get('next_suggested_task','')}")

if __name__ == "__main__":
    main()
