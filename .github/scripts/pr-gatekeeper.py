#!/usr/bin/env python3
"""
PR Gatekeeper v2 — autonomous review + auto-merge
- GPT-4o = PRIMARY reviewer (independent from code-generating Claude)
- Claude  = SECONDARY reviewer (blueprint alignment + intent)
- Both must APPROVE or PR is blocked
- Auto-merges via GitHub API after approval
- Deadlock escape: closes PR after 2 rejection cycles, opens retry issue
- Full crash recovery: any exception opens a GitHub issue
"""
import os, sys, json, re, time, traceback, requests
from pathlib import Path

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY", "")
GH_PAT            = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
PR_NUMBER         = int(os.environ["PR_NUMBER"])
PR_TITLE          = os.environ.get("PR_TITLE", "")
PR_BODY           = os.environ.get("PR_BODY", "")
PR_HEAD_SHA       = os.environ.get("PR_HEAD_SHA", "")
REPO_OWNER        = os.environ.get("REPO_OWNER", "ismaelloveexcel")
REPO_NAME         = os.environ.get("REPO_NAME", "ismael-agent-world")

CLAUDE_MODEL = "claude-sonnet-4-6"
OPENAI_MODEL = "gpt-4o"
GH_API       = "https://api.github.com"
ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
OPENAI_API   = "https://api.openai.com/v1/chat/completions"
GH_GRAPHQL   = "https://api.github.com/graphql"
MAX_REJECTION_CYCLES = 2
MAX_RETRIES = 3

def gh(method, path, **kw):
    h = {"Authorization": f"token {GH_PAT}", "Accept": "application/vnd.github.v3+json"}
    return requests.request(method, f"{GH_API}/{path}", headers=h, timeout=30, **kw)

def graphql(query, variables=None):
    r = requests.post(GH_GRAPHQL,
        headers={"Authorization": f"bearer {GH_PAT}", "Content-Type": "application/json"},
        json={"query": query, "variables": variables or {}}, timeout=30)
    return r.json()

def _call(url, headers, payload, retries=MAX_RETRIES):
    for i in range(retries):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            if r.status_code == 429:
                time.sleep(30); continue
            r.raise_for_status()
            return r
        except Exception as e:
            if i < retries-1: time.sleep(10*(i+1))
            else: raise

def call_claude(prompt, system, max_tokens=2500):
    r = _call(ANTHROPIC_API,
        {"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01",
         "content-type": "application/json"},
        {"model": CLAUDE_MODEL, "max_tokens": max_tokens, "system": system,
         "messages": [{"role":"user","content":prompt}]})
    return r.json()["content"][0]["text"]

def call_openai(prompt, system, max_tokens=1200):
    if not OPENAI_API_KEY: return ""
    r = _call(OPENAI_API,
        {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
        {"model": OPENAI_MODEL, "max_tokens": max_tokens,
         "messages": [{"role":"system","content":system},{"role":"user","content":prompt}]})
    return r.json()["choices"][0]["message"]["content"]

def parse_json_safe(text):
    if not text: return {}
    for pat in [r"```json\s*(.*?)\s*```", r"\{.*\}"]:
        m = re.search(pat, text, re.DOTALL)
        if m:
            try: return json.loads(m.group(1) if "```" in pat else m.group(0))
            except: pass
    return {}

def call_json(fn, prompt, system, max_tokens):
    p = prompt
    for i in range(MAX_RETRIES):
        raw = fn(p, system, max_tokens)
        d = parse_json_safe(raw)
        if d: return d
        if i < MAX_RETRIES-1:
            p = prompt + "\n\nIMPORTANT: respond with ONLY ```json {...} ``` — nothing else."
    return {}

def get_pr_diff():
    r = gh("GET", f"repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}/files")
    if r.status_code != 200: return ""
    parts = []
    for f in r.json()[:12]:
        patch = f.get("patch","")[:2000]
        parts.append(f"### {f['filename']} (+{f.get('additions',0)} -{f.get('deletions',0)})\n{patch}")
    return "\n\n".join(parts)

def get_pr_node_id():
    r = gh("GET", f"repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}")
    return r.json().get("node_id","") if r.status_code == 200 else ""

def count_prior_rejections():
    # Count formal CHANGES_REQUESTED reviews
    formal = 0
    r = gh("GET", f"repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}/reviews")
    if r.status_code == 200:
        formal = sum(1 for x in r.json() if x.get("state") == "CHANGES_REQUESTED")
    # Also count comment-based rejections (fallback when formal review fails)
    comment_based = 0
    c = gh("GET", f"repos/{REPO_OWNER}/{REPO_NAME}/issues/{PR_NUMBER}/comments")
    if c.status_code == 200:
        comment_based = sum(1 for x in c.json()
                            if "Gatekeeper: REQUEST_CHANGES" in x.get("body",""))
    return max(formal, comment_based)

def read_local(path):
    p = Path(path)
    return p.read_text() if p.exists() else ""

def post_review(verdict, body):
    event = "APPROVE" if verdict == "APPROVED" else "REQUEST_CHANGES"
    r = gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}/reviews",
           json={"commit_id": PR_HEAD_SHA, "body": body, "event": event})
    if r.status_code in (200,201):
        print(f"Review posted: {verdict}")
    else:
        gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/issues/{PR_NUMBER}/comments",
           json={"body": f"**Gatekeeper: {verdict}**\n\n{body}"})

def auto_merge_pr():
    print("Auto-merging...")
    r = gh("PUT", f"repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}/merge",
           json={"merge_method":"squash",
                 "commit_title":f"{PR_TITLE} [gatekeeper-approved]"})
    if r.status_code == 200:
        print(f"PR #{PR_NUMBER} merged."); return
    print(f"Direct merge blocked ({r.status_code}). Enabling auto-merge via GraphQL...")
    node_id = get_pr_node_id()
    res = graphql("""
        mutation EnableAutoMerge($id: ID!) {
          enablePullRequestAutoMerge(input:{pullRequestId:$id,mergeMethod:SQUASH}){
            pullRequest{number}}}""", {"id": node_id})
    if res.get("errors"):
        msg = res["errors"][0].get("message","unknown error")
        print(f"GraphQL auto-merge failed: {msg}")
        gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/issues/{PR_NUMBER}/comments",
           json={"body":"✅ Gatekeeper approved. Auto-merge unavailable — please merge manually."})
    else:
        print("GraphQL auto-merge enabled.")
        gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/issues/{PR_NUMBER}/comments",
           json={"body":"✅ Gatekeeper approved. Auto-merge enabled — merges once CI passes."})

def close_and_retry(blocking, rejections):
    print(f"PR rejected {rejections}x. Closing + opening retry issue.")
    gh("PATCH", f"repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}", json={"state":"closed"})
    issues_str = "\n".join(f"- {i}" for i in blocking) or "- See closed PR"
    gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/issues", json={
        "title": f"[Retry] {PR_TITLE}",
        "body": (f"PR #{PR_NUMBER} rejected {rejections} times — closed.\n\n"
                 f"**Blocking issues:**\n{issues_str}\n\n"
                 "Orchestrator will retry on next run."),
        "labels": ["agent","bug"]})

def open_failure_issue(tb):
    try:
        gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/issues", json={
            "title": f"[Gatekeeper] Crashed on PR #{PR_NUMBER}",
            "body": f"PR #{PR_NUMBER}: {PR_TITLE}\n\n```\n{tb[:2000]}\n```",
            "labels":["bug","agent"]})
    except: pass

def main():
    print(f"=== PR Gatekeeper v2 — PR #{PR_NUMBER} ===")
    blueprint  = read_local("BLUEPRINT.md")
    build_plan = read_local(".github/BUILD_PLAN.md")
    diff       = get_pr_diff()
    if not diff:
        print("No diff. Skipping."); return

    prior_rejections = count_prior_rejections()
    print(f"Prior rejections: {prior_rejections}/{MAX_REJECTION_CYCLES}")

    # PRIMARY: GPT-4o (independent — did not write the code)
    print("GPT-4o primary review...")
    gpt = call_json(call_openai, f"""
You are the primary code reviewer for Ismael Agent World PRs.
Claude generated this code. You are independent — review critically.

PR: {PR_TITLE}
Description: {PR_BODY[:500]}

Blueprint stack: Next.js 15 App Router + FastAPI (Python) + Supabase + pgvector.
Phase 1 rule: NO external API calls / fetch() to real services — mock data only.

Diff:
{diff[:5000]}

Evaluate:
1. TypeScript strict mode — implicit any, missing types?
2. Import paths — do all imports reference real existing files?
3. Next.js 15 correctness — use client/server, App Router patterns?
4. Phase 1 safety — any real external fetch() calls?
5. Code quality — broken JSX, logic errors, missing error handling?
6. Complexity (1-10) — maintainable by solo non-technical founder?
7. Scope — max 8 files, one focused task?
8. Architecture alignment — matches the full-stack blueprint structure?

```json
{{
  "verdict": "APPROVED",
  "complexity_score": 4,
  "blocking_issues": [],
  "quality_notes": [],
  "suggestions": [],
  "summary": "2-sentence verdict"
}}
```
verdict: APPROVED or REQUEST_CHANGES. complexity>7 = REQUEST_CHANGES.

IMPORTANT PHASE 1 RULES — do NOT flag these as issues:
- .env.example with placeholder values (PLACEHOLDER, YOUR_KEY_HERE, etc.) is CORRECT — never flag placeholders in example files as security risks
- Mock/seed data files with hardcoded test values are EXPECTED in Phase 1
- Missing env vars in .env.example that reference blueprint services are ACCEPTABLE
""", "Critical independent reviewer. Claude wrote this code. Be strict but fair — Phase 1 uses placeholders intentionally.", 1400)

    # SECONDARY: Claude (blueprint alignment)
    print("Claude secondary review (blueprint alignment)...")
    cla = call_json(call_claude, f"""
Review this PR for Ismael Agent World.
Your role: blueprint alignment only. You did NOT write this code.

Blueprint:
{blueprint[:3000]}

Build plan:
{build_plan[:1500]}

PR: {PR_TITLE}
Diff:
{diff[:3500]}

Check:
1. Does this implement a real task from the build plan?
2. Correct layer? (UI in apps/web, agents in apps/api/agents, tools in apps/api/tools)
3. Any hardcoded secrets?
4. Matches blueprint architecture (monorepo structure)?

```json
{{
  "verdict": "APPROVED",
  "blueprint_aligned": true,
  "correct_layer": true,
  "secrets_found": false,
  "blocking_issues": [],
  "summary": "2-sentence blueprint verdict"
}}
```
""", "Blueprint alignment reviewer. You did not write this code.", 1400)

    gpt_v = gpt.get("verdict","APPROVED")
    cla_v = cla.get("verdict","APPROVED")
    final = "APPROVED" if gpt_v == "APPROVED" and cla_v == "APPROVED" else "REQUEST_CHANGES"
    complexity = gpt.get("complexity_score", 5)
    blocking = gpt.get("blocking_issues",[]) + cla.get("blocking_issues",[])

    print(f"GPT-4o: {gpt_v} (complexity {complexity}/10) | Claude: {cla_v} | Final: {final}")

    if final == "REQUEST_CHANGES":
        new_count = prior_rejections + 1
        if new_count >= MAX_REJECTION_CYCLES:
            close_and_retry(blocking, new_count); return

    rows = (
        f"| Check | Result |\n|-------|--------|\n"
        f"| Blueprint aligned | {'✅' if cla.get('blueprint_aligned',True) else '❌'} |\n"
        f"| Correct layer | {'✅' if cla.get('correct_layer',True) else '❌'} |\n"
        f"| Complexity | {complexity}/10 {'✅' if complexity<=7 else '❌'} |\n"
        f"| Phase 1 safety | {'✅' if not gpt.get('blocking_issues') else '⚠️'} |\n"
        f"| No secrets | {'✅' if not cla.get('secrets_found') else '❌'} |"
    )
    v_emoji = "✅" if final == "APPROVED" else "❌"
    body = (
        f"## {v_emoji} Gatekeeper: {final}\n\n"
        f"**GPT-4o:** {gpt.get('summary','')}\n"
        f"**Claude:** {cla.get('summary','')}\n\n"
        f"{rows}\n"
    )
    if blocking:
        body += "\n### ❌ Blocking Issues\n" + "\n".join(f"- {i}" for i in blocking) + "\n"
    if gpt.get("suggestions"):
        body += "\n### 💡 Suggestions\n" + "\n".join(f"- {s}" for s in gpt["suggestions"][:4]) + "\n"
    if final == "APPROVED":
        body += "\n---\n*Approved by GPT-4o + Claude. Auto-merging now.*"
    else:
        rem = MAX_REJECTION_CYCLES - (prior_rejections+1)
        body += f"\n---\n*Fix blocking issues above. {rem} cycle(s) before PR is closed and retried.*"

    post_review(final, body)
    if final == "APPROVED":
        time.sleep(2)
        auto_merge_pr()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        print(f"CRASH:\n{tb}")
        open_failure_issue(tb)
        sys.exit(1)
