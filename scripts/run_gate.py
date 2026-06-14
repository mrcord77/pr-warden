#!/usr/bin/env python3
"""PR Warden gate engine — the complete rules.md engine as plain Python.
Reads a payload JSON (schema below, or extract_pr_payload.py --json), prints the
verdict, exits with a CI-actionable code:
0 = PASS, 78 = RE-ANCHOR, 75 = NEEDS-PROVENANCE, 1 = BLOCK, 2 = ESCALATION.

No AI anywhere in this file. Every check is the boolean test written in rules.md.
The one rule requiring semantic reading (Trigger 2, self-contradicting ticket) is
not implemented here and is reported as NOT EVALUATED.

Payload schema:
{ "ticket": {"id","description","criteria":[],"paths":[],"assignee","status"},
  "pr": {"number","author","title","body","draft",commits":[],"files":[],"new_dependencies":[]},
  "second_pr": {"number","author","title","files":[]} }            # optional
"""
import argparse, json, os, re, sys

def load_config():
    path = os.path.join(os.path.dirname(__file__), "..", "config.md")
    cfg = {}
    if os.path.exists(path):
        for k, v in re.findall(r"\|\s*([a-z_]+)\s*\|\s*([0-9.]+)\s*\|", open(path).read()):
            cfg[k] = float(v)
    return cfg

CFG = load_config()
def cv(k, d): return CFG.get(k, d)
def norm(x): return (x or "").lstrip("@").strip()

def gate(p):
    log = []
    def fired(label, hit, detail):
        log.append(("FIRED      " if hit else "NOT FIRED  ") + label + " — " + detail)
    t, pr = p.get("ticket") or {}, p.get("pr") or {}
    criteria = t.get("criteria") or []
    commits = pr.get("commits") or []
    files = pr.get("files") or []

    log.append("— STEP 1 ESCALATION AUDIT —")
    q = p.get("second_pr")
    dup = bool(q) and q.get("title") == pr.get("title") and \
          sorted(q.get("files") or []) == sorted(files) and bool(files)
    fired("Trigger 1 duplicate-agent submission", dup,
          "same ticket + identical title + identical file list" if dup else "conditions not all satisfied")
    log.append("Trigger 2 (contradictory baseline): NOT EVALUATED — semantic test, full operator only.")
    if dup:
        return {"directive": "ESCALATION: COORDINATED DUPLICATE SUBMISSION — HUMAN REVIEW REQUIRED",
                "bis": None, "tds": None, "log": log, "exit": 2,
                "detail": f"PRs {pr.get('number')} ({norm(pr.get('author'))}) and {q.get('number')} ({norm(q.get('author'))})"}

    log.append("— STEP 2 BASELINE PRESENCE —")
    tid = (t.get("id") or "").strip()
    if not tid:
        return {"directive": "BLOCK", "bis": None, "tds": None, "log": log, "exit": 1,
                "detail": "No ticket ID — no baseline to measure against."}
    log.append(f"Ticket ID {tid} present. Continue.")

    log.append("— STEP 3 BIS (start 1.00) —")
    bis = 1.00
    b1 = not (t.get("description") or "").strip() and not criteria
    if b1: bis -= cv("empty_ticket", .30)
    fired("B1 empty ticket", b1, "no description AND no criteria" if b1 else "baseline content present")
    body = pr.get("body") or ""
    b2 = len(body) < 50
    if b2: bis -= cv("thin_pr_body", .20)
    fired("B2 PR body < 50 chars", b2, f"{len(body)} chars")
    junk = sum(1 for c in commits if len(c.strip()) < 10)
    b3 = min(junk * cv("junk_commit", .10), cv("junk_commit_cap", .30))
    bis -= b3
    fired("B3 junk commits (<10 chars)", junk > 0, f"{junk} of {len(commits)} -> -{b3:.2f}")
    b4 = (t.get("status") or "").strip().lower() in ("closed", "done")
    if b4: bis -= cv("closed_ticket", .20)
    fired("B4 ticket Closed/Done", b4, t.get("status") or "(absent)")
    b5 = bool(pr.get("draft"))
    if b5: bis -= cv("draft_pr", .15)
    fired("B5 draft PR", b5, "draft" if b5 else "not draft")
    bis = round(bis, 2)
    log.append(f"Final BIS = {bis:.2f}")

    log.append("— STEP 4 TDS (start 0.00) —")
    tds = 0.0
    hay = " ".join([pr.get("title") or "", body] + commits)
    d1 = tid not in hay
    if d1: tds += cv("no_ticket_ref", .15)
    fired("D1 ticket ID absent from title+body+commits", d1, "+0.15" if d1 else "referenced")
    unaddressed = 0
    for i, c in enumerate(criteria):
        if f"({i+1})" not in body and c.lower()[:30] not in body.lower():
            unaddressed += 1
    d2 = min(unaddressed * cv("unaddressed_criterion", .10), cv("unaddressed_criterion_cap", .30))
    tds += d2
    fired("D2 unaddressed criteria", unaddressed > 0, f"{unaddressed} of {len(criteria)} -> +{d2:.2f}")
    paths = t.get("paths") or []
    if not paths:
        fired("D3 out-of-scope files", False, "SKIPPED — ticket declares no paths; scope is never inferred")
    else:
        oos = sum(1 for f in files if not any(f.startswith(x) for x in paths))
        d3 = min(oos * cv("oos_file", .10), cv("oos_file_cap", .30))
        tds += d3
        fired("D3 out-of-scope files", oos > 0, f"{oos} of {len(files)} outside {paths} -> +{d3:.2f}")
    deps = pr.get("new_dependencies") or []
    t_hay = ((t.get("description") or "") + " " + " ".join(criteria)).lower()
    und = sum(1 for d in deps if d.lower() not in t_hay)
    d4 = min(und * cv("undeclared_dep", .10), cv("undeclared_dep_cap", .20))
    tds += d4
    fired("D4 undeclared dependencies", und > 0, f"{und} of {len(deps)} -> +{d4:.2f}")
    m = re.match(r"^([A-Za-z]+-)", tid)
    foreign = 0
    if m:
        for c in commits:
            ids = re.findall(re.escape(m.group(1)) + r"\d+", c)
            if ids and any(x != tid for x in ids):
                foreign += 1
    d5 = min(foreign * cv("foreign_ticket_commit", .15), cv("foreign_ticket_cap", .30))
    tds += d5
    fired("D5 commits referencing a different ticket", foreign > 0, f"{foreign} commit(s) -> +{d5:.2f}")
    assignee = norm(t.get("assignee"))
    if not assignee:
        fired("D6 author ≠ assignee", False, "SKIPPED — no assignee on ticket")
    else:
        d6 = norm(pr.get("author")) != assignee
        if d6: tds += cv("author_not_assignee", .10)
        fired("D6 author ≠ assignee", d6, f"{norm(pr.get('author'))} vs {assignee}")
    tds = min(round(tds, 2), 1.00)
    log.append(f"Final TDS = {tds:.2f}")

    log.append("— STEP 5 PRECEDENCE —")
    if tds > cv("block_threshold", .55):
        d, code = "BLOCK", 1
    elif bis < cv("bis_floor", .70):
        d, code = "NEEDS-PROVENANCE", 75
    elif tds > cv("reanchor_threshold", .35):
        d, code = "RE-ANCHOR", 78
    else:
        d, code = "PASS", 0
    log.append(f"BIS {bis:.2f} / TDS {tds:.2f} -> {d}")
    return {"directive": d, "bis": bis, "tds": tds, "log": log, "exit": code, "detail": ""}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("payload", help="payload JSON file, or - for stdin")
    ap.add_argument("--markdown", action="store_true")
    a = ap.parse_args()
    data = json.load(sys.stdin if a.payload == "-" else open(a.payload))
    r = gate(data)
    if a.markdown:
        gh_map = {"PASS": "success", "RE-ANCHOR": "neutral + comment + label drift:re-anchor",
                  "NEEDS-PROVENANCE": "neutral + comment", "BLOCK": "failure"}
        gh = gh_map.get(r["directive"], "failure — human review")
        print("# PR WARDEN VERDICT\n[PR-WARDEN SPEC-v0.1 / deterministic engine]\n")
        print(f"## DIRECTIVE\n```\n{r['directive']}\n```\nGitHub check state: {gh}\n")
        if r["bis"] is not None:
            print(f"## SCORES\n* **BIS:** {r['bis']:.2f} (floor 0.70)\n* **TDS:** {r['tds']:.2f} (re-anchor 0.35 / block 0.55)\n")
        else:
            print("## SCORES\n* not scored — short-circuit\n")
        if r["detail"]: print(r["detail"] + "\n")
        print("## EXECUTION LOG\n```")
        print("\n".join(r["log"]))
        print("```")
    else:
        print(json.dumps({k: r[k] for k in ("directive", "bis", "tds")}, ensure_ascii=False))
    sys.exit(r["exit"])

if __name__ == "__main__":
    main()
