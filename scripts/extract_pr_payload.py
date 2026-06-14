#!/usr/bin/env python3
"""PR Warden payload extractor — turn a real PR (and its linked GitHub Issue) into
a gate-ready payload.

Usage:
  python scripts/extract_pr_payload.py --repo owner/name --pr 87              # human paste format
  python scripts/extract_pr_payload.py --repo owner/name --pr 87 --json      # run_gate.py format
  ... [--issue 42]   # force the ticket issue; otherwise auto-detected from
                     # "Closes/Fixes/Resolves #N" in the PR body

Requires the GitHub CLI (`gh`) authenticated. Nothing is invented: structures the
issue doesn't carry are emitted absent and take their rules.md SKIPs/deductions.
Ticket convention: reference/ticket_convention.md.
"""
import argparse, json, re, subprocess, sys

DEP_MANIFESTS = ("package.json", "requirements.txt", "Cargo.toml", "go.mod", "pyproject.toml")
CLOSES = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", re.IGNORECASE)

def gh(args):
    r = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"gh error: {r.stderr.strip()}")
    return r.stdout

def parse_issue_body(body):
    """Apply the ticket convention to a raw issue body. Pure function — tested."""
    body = body or ""
    criteria = [m.group(1).strip() for m in re.finditer(r"^\s*[-*]\s*\[[ xX]\]\s*(.+)$", body, re.MULTILINE)]
    paths = []
    pm = re.search(r"^\s*Paths:\s*(.+)$", body, re.MULTILINE)
    if pm:
        paths = [p.strip() for p in pm.group(1).split(",") if p.strip()]
    desc_lines = []
    for line in body.splitlines():
        if re.match(r"^\s*[-*]\s*\[[ xX]\]", line): continue
        if re.match(r"^\s*Paths:", line): continue
        if re.match(r"^\s*#{1,6}\s*acceptance criteria", line, re.IGNORECASE): continue
        desc_lines.append(line)
    return {"description": "\n".join(desc_lines).strip(), "criteria": criteria, "paths": paths}

def detect_issue(pr_body, flag):
    if flag: return str(flag)
    m = CLOSES.search(pr_body or "")
    return m.group(1) if m else None

def added_dependencies(repo, pr_number, files):
    """Names of packages added in dependency-manifest diffs (best effort, additive lines only)."""
    deps = []
    manifest_files = [f for f in files if any(f.endswith(m) for m in DEP_MANIFESTS)]
    if not manifest_files: return deps
    diff = gh(["pr", "diff", str(pr_number), "--repo", repo])
    for line in diff.splitlines():
        if not line.startswith("+") or line.startswith("+++"): continue
        m = re.match(r'^\+\s*"([A-Za-z0-9@/_.-]+)"\s*:', line) or \
            re.match(r"^\+\s*([A-Za-z0-9_.-]+)\s*[=><~^]", line) or \
            re.match(r"^\+\s*([A-Za-z0-9_.-]+)\s*=\s*\"", line)
        if m and m.group(1) not in deps:
            deps.append(m.group(1))
    return deps

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", required=True)
    ap.add_argument("--issue", help="issue number override")
    ap.add_argument("--json", action="store_true", help="emit run_gate.py payload JSON")
    a = ap.parse_args()

    pr = json.loads(gh(["pr", "view", str(a.pr), "--repo", a.repo, "--json",
                        "number,title,body,author,isDraft,commits,files"]))
    files = [f["path"] for f in pr["files"]]
    commits = [c["messageHeadline"] for c in pr["commits"]]

    issue_num = detect_issue(pr.get("body"), a.issue)
    ticket = {"id": "", "description": "", "criteria": [], "paths": [], "assignee": "", "status": ""}
    if issue_num:
        iss = json.loads(gh(["issue", "view", issue_num, "--repo", a.repo, "--json",
                             "number,title,body,assignees,state"]))
        parsed = parse_issue_body(iss.get("body"))
        ticket = {"id": f"#{iss['number']}",
                  "description": (iss.get("title") or "") + ("\n" + parsed["description"] if parsed["description"] else ""),
                  "criteria": parsed["criteria"], "paths": parsed["paths"],
                  "assignee": (iss["assignees"][0]["login"] if iss.get("assignees") else ""),
                  "status": iss.get("state", "")}

    payload = {"ticket": ticket,
               "pr": {"number": f"#{pr['number']}", "author": pr["author"]["login"],
                      "title": pr["title"], "body": pr.get("body") or "",
                      "draft": pr["isDraft"], "commits": commits, "files": files,
                      "new_dependencies": added_dependencies(a.repo, a.pr, files)}}

    if a.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    t = payload["ticket"]
    out = ["Ticket " + (t["id"] or "(NONE DETECTED — gate will BLOCK)") + " — \"" + t["description"].splitlines()[0] + "\"" if t["id"] else "Ticket: (none detected)"]
    if t["criteria"]: out.append("Criteria: " + "; ".join(f"({i+1}) {c}" for i, c in enumerate(t["criteria"])))
    if t["paths"]: out.append("Paths: " + ", ".join(t["paths"]))
    if t["assignee"]: out.append("Assignee: @" + t["assignee"] + ". Status: " + t["status"])
    p = payload["pr"]
    out += ["", "PR payload:", f"PR {p['number']} | author @{p['author']} | draft: {p['draft']}",
            f'title: "{p["title"]}"', f'body ({len(p["body"])} chars): "{p["body"][:500]}"', "commits:"]
    out += [f'  "{c}"' for c in p["commits"]]
    out.append("files:")
    out += [f"  {f}" for f in p["files"]]
    if p["new_dependencies"]: out.append("new dependencies: " + ", ".join(p["new_dependencies"]))
    print("\n".join(out))

if __name__ == "__main__":
    main()
