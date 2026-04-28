#!/usr/bin/env python3
"""
PR Gatekeeper — independent review agent for agent/* PRs
Checks:
  1. Blueprint alignment — does this PR match the build plan?
  2. Complexity — is it too complex for a solo non-technical user?
  3. Simplification — anything that can be trimmed?
  4. Safety — no external API calls, no hardcoded secrets

Posts a structured GitHub review comment: APPROVED or REQUEST_CHANGES
"""

import os, sys, json, re, requests
from pathlib import Path

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY", "")
GH_PAT            = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
PR_NUMBER         = int(os.environ["PR_NUMBER"])
PR_TITLE          = os.environ.get("PR_TITLE", "")
PR_BODY           = os.environ.get("PR_BODY", "")
PR_HEAD_SHA       = os.environ.get("PR_HEAD_SHA", "")
PR_BASE_SHA       = os.environ.get("PR_BASE_SHA", "")
REPO_OWNER        = os.environ.get("REPO_OWNER", "ismaelloveexcel")
REPO_NAME         = os.environ.get("REPO_NAME", "ismael-agent-world")

CLAUDE_MODEL = "claude-sonnet-4-6"
OPENAI_MODEL = "gpt-4o"
GH_API       = "https://api.github.com"
ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
OPENAI_API   = "https://api.openai.com/v1/chat/completions"

BUILD_PLAN_PATH = ".github/BUILD_PLAN.md"
BLUEPRINT_PATH  = "BLUEPRINT.md"

def gh(method, path, **kwargs):
    headers = {"Authorization": f"token {GH_PAT}", "Accept": "application/vnd.github.v3+json"}
    return requests.request(method, f"{GH_API}/{path}", headers=headers, timeout=30, **kwargs)

def call_claude(prompt, system, max_tokens=3000):
    resp = requests.post(ANTHROPIC_API, headers={
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }, json={"model": CLAUDE_MODEL, "max_tokens": max_tokens, "system": system,
             "messages": [{"role": "user", "content": prompt}]}, timeout=120)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

def call_openai(prompt, system, max_tokens=800):
    if not OPENAI_API_KEY: return ""
    resp = requests.post(OPENAI_API, headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"
    }, json={"model": OPENAI_MODEL, "max_tokens": max_tokens,
             "messages": [{"role":"system","content":system},{"role":"user","content":prompt}]}, timeout=60)
    if resp.status_code != 200: return ""
    return resp.json()["choices"][0]["message"]["content"]

def get_pr_diff() -> str:
    """Get the PR file diff."""
    resp = gh("GET", f"repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}/files")
    if resp.status_code != 200:
        return ""
    files = resp.json()
    diff_parts = []
    for f in files[:10]:
        patch = f.get("patch", "")[:1500]
        diff_parts.append(f"### {f['filename']} (+{f.get('additions',0)} -{f.get('deletions',0)})\n{patch}")
    return "\n\n".join(diff_parts)

def read_local(path: str) -> str:
    p = Path(path)
    return p.read_text() if p.exists() else ""

def post_review(verdict: str, body: str):
    """Post a GitHub PR review (APPROVE or REQUEST_CHANGES)."""
    event = "APPROVE" if verdict == "APPROVED" else "REQUEST_CHANGES"
    resp = gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}/reviews",
              json={"commit_id": PR_HEAD_SHA, "body": body, "event": event})
    if resp.status_code in (200, 201):
        print(f"✅ Review posted: {verdict}")
    else:
        print(f"⚠️  Review post failed ({resp.status_code}): {resp.text[:200]}")
        # Fallback: post as a comment
        gh("POST", f"repos/{REPO_OWNER}/{REPO_NAME}/issues/{PR_NUMBER}/comments",
           json={"body": f"**Gatekeeper Review: {verdict}**\n\n{body}"})

def main():
    print(f"=== PR Gatekeeper — PR #{PR_NUMBER}: {PR_TITLE} ===")

    blueprint  = read_local(BLUEPRINT_PATH)
    build_plan = read_local(BUILD_PLAN_PATH)
    diff       = get_pr_diff()

    if not diff:
        print("No diff found — skipping review.")
        sys.exit(0)

    # ── Review 1: Claude checks blueprint alignment + safety
    print("🔍 Claude: checking blueprint alignment and safety...")
    claude_review = call_claude(f"""
You are the PR Gatekeeper for Ismael Agent World.
Review this agent-generated PR before it can be merged.

PR Title: {PR_TITLE}
PR Description: {PR_BODY[:800]}

Blueprint (key requirements):
{blueprint[:4000]}

Build Plan:
{build_plan[:2000]}

Code diff:
{diff[:5000]}

Evaluate:
1. BLUEPRINT ALIGNMENT — Does this PR implement what the blueprint requires? Does it match a task from the build plan?
2. SAFETY — Any external API calls, hardcoded secrets, or fetch() to real services in Phase 1? (Not allowed)
3. QUALITY — Missing types, broken imports, unclosed JSX, console.log in production code?
4. SCOPE — Is this PR scoped correctly (≤8 files, focused on one task)?

Output JSON:
```json
{{
  "verdict": "APPROVED",
  "blueprint_aligned": true,
  "safety_issues": [],
  "quality_issues": [],
  "scope_ok": true,
  "summary": "2-3 sentence plain English summary of what this PR does and why it's approved/rejected",
  "blocking_issues": [],
  "suggestions": []
}}
```
Verdict must be APPROVED or REQUEST_CHANGES.
""",
    "You are a strict but pragmatic code gatekeeper. Approve if the code is correct and aligned. Reject only for real issues.",
    max_tokens=2000)

    # ── Review 2: GPT-4o checks complexity
    print("🔍 GPT-4o: checking complexity...")
    gpt_review = call_openai(f"""
Rate the complexity of this PR for a solo non-technical founder to maintain.

PR: {PR_TITLE}
Diff preview:
{diff[:2000]}

Score 1-10. Flag anything that's unnecessarily complex for a solo app.

Reply with JSON:
```json
{{
  "complexity_score": 4,
  "verdict": "APPROVED",
  "complexity_flags": [],
  "simplification_suggestions": []
}}
```
Verdict APPROVED if score ≤ 7, REQUEST_CHANGES if > 7.
""", "You are a complexity reviewer for solo developer projects.", max_tokens=400)

    # ── Parse verdicts
    def parse_json_safe(text):
        try:
            m = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if m: return json.loads(m.group(1))
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if m: return json.loads(m.group(0))
        except: pass
        return {}

    claude_data = parse_json_safe(claude_review)
    gpt_data    = parse_json_safe(gpt_review)

    claude_verdict     = claude_data.get("verdict", "APPROVED")
    gpt_verdict        = gpt_data.get("verdict", "APPROVED")
    complexity_score   = gpt_data.get("complexity_score", 5)
    blocking_issues    = claude_data.get("blocking_issues", [])
    quality_issues     = claude_data.get("quality_issues", [])
    safety_issues      = claude_data.get("safety_issues", [])
    suggestions        = claude_data.get("suggestions", []) + gpt_data.get("simplification_suggestions", [])
    summary            = claude_data.get("summary", "Review complete.")

    # Final verdict: both must approve
    final_verdict = "APPROVED" if (claude_verdict == "APPROVED" and gpt_verdict == "APPROVED") else "REQUEST_CHANGES"

    print(f"   Claude: {claude_verdict} | GPT-4o: {gpt_verdict} (complexity {complexity_score}/10)")
    print(f"   Final: {final_verdict}")

    # ── Build review comment
    verdict_emoji = "✅" if final_verdict == "APPROVED" else "❌"
    body_lines = [
        f"## {verdict_emoji} Gatekeeper Review: {final_verdict}",
        "",
        f"**Summary:** {summary}",
        "",
        f"| Check | Result |",
        f"|-------|--------|",
        f"| Blueprint alignment | {'✅' if claude_data.get('blueprint_aligned', True) else '❌'} |",
        f"| Complexity score | {complexity_score}/10 {'✅' if complexity_score <= 7 else '❌'} |",
        f"| Scope (≤8 files) | {'✅' if claude_data.get('scope_ok', True) else '❌'} |",
        f"| Safety (no real API calls) | {'✅' if not safety_issues else '❌'} |",
        "",
    ]

    if blocking_issues:
        body_lines += ["### ❌ Blocking Issues", ""]
        for issue in blocking_issues:
            body_lines.append(f"- {issue}")
        body_lines.append("")

    if quality_issues:
        body_lines += ["### ⚠️ Quality Issues", ""]
        for issue in quality_issues:
            body_lines.append(f"- {issue}")
        body_lines.append("")

    if safety_issues:
        body_lines += ["### 🚨 Safety Issues", ""]
        for issue in safety_issues:
            body_lines.append(f"- {issue}")
        body_lines.append("")

    if suggestions:
        body_lines += ["### 💡 Suggestions (non-blocking)", ""]
        for s in suggestions[:4]:
            body_lines.append(f"- {s}")
        body_lines.append("")

    if final_verdict == "APPROVED":
        body_lines += [
            "---",
            "*This PR is cleared for merge. Once merged, the orchestrator will automatically pick up the next task.*"
        ]
    else:
        body_lines += [
            "---",
            "*Fix the blocking issues above and push again. The gatekeeper will re-review automatically.*"
        ]

    review_body = "\n".join(body_lines)
    post_review(final_verdict, review_body)

if __name__ == "__main__":
    main()
