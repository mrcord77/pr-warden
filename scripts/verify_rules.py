#!/usr/bin/env python3
"""PR Warden reference scorer — model-free referee.
Reimplements the rules.md tables as plain code. If examples.md numbers can't be
reproduced here, the rules aren't deterministic. Reads config.md when present."""
import os, re

def load_config():
    path = os.path.join(os.path.dirname(__file__), "..", "config.md")
    cfg = {}
    if os.path.exists(path):
        for k, v in re.findall(r"\|\s*([a-z_]+)\s*\|\s*([0-9.]+)\s*\|", open(path).read()):
            cfg[k] = float(v)
    return cfg

CFG = load_config()
def cv(k, d): return CFG.get(k, d)

def bis(findings):
    """findings: dict of test->count (junk_commit may be >1)."""
    s = 1.00
    s -= cv("empty_ticket", .30) if findings.get("empty_ticket") else 0
    s -= cv("thin_pr_body", .20) if findings.get("thin_pr_body") else 0
    s -= min(findings.get("junk_commit", 0) * cv("junk_commit", .10), cv("junk_commit_cap", .30))
    s -= cv("closed_ticket", .20) if findings.get("closed_ticket") else 0
    s -= cv("draft_pr", .15) if findings.get("draft_pr") else 0
    return round(s, 2)

def tds(findings):
    s = 0.0
    s += cv("no_ticket_ref", .15) if findings.get("no_ticket_ref") else 0
    s += min(findings.get("unaddressed_criterion", 0) * cv("unaddressed_criterion", .10), cv("unaddressed_criterion_cap", .30))
    s += min(findings.get("oos_file", 0) * cv("oos_file", .10), cv("oos_file_cap", .30))
    s += min(findings.get("undeclared_dep", 0) * cv("undeclared_dep", .10), cv("undeclared_dep_cap", .20))
    s += min(findings.get("foreign_ticket_commit", 0) * cv("foreign_ticket_commit", .15), cv("foreign_ticket_cap", .30))
    s += cv("author_not_assignee", .10) if findings.get("author_not_assignee") else 0
    return min(round(s, 2), 1.00)

def directive(escalation, no_ticket, b, t):
    if escalation: return "ESCALATION"
    if no_ticket: return "BLOCK"
    if t > cv("block_threshold", .55): return "BLOCK"
    if b < cv("bis_floor", .70): return "NEEDS-PROVENANCE"
    if cv("reanchor_threshold", .35) < t <= cv("block_threshold", .55): return "RE-ANCHOR"
    return "PASS"

cases = {
    "Case 1 clean (expect BIS 1.00, TDS 0.00, PASS)":
        (False, False, {}, {}, 1.00, 0.00, "PASS"),
    "Case 2 hygiene fail (expect BIS 0.50, TDS 0.10, NEEDS-PROVENANCE)":
        (False, False, {"thin_pr_body": 1, "junk_commit": 3}, {"unaddressed_criterion": 1}, 0.50, 0.10, "NEEDS-PROVENANCE"),
    "Case 3 silent drift (expect BIS 1.00, TDS 0.45, RE-ANCHOR)":
        (False, False, {}, {"no_ticket_ref": 1, "oos_file": 2, "undeclared_dep": 1}, 1.00, 0.45, "RE-ANCHOR"),
    "Case 4 wrong-ticket PR (expect BIS 1.00, TDS 0.65, BLOCK)":
        (False, False, {}, {"no_ticket_ref": 1, "foreign_ticket_commit": 2, "author_not_assignee": 1, "unaddressed_criterion": 1}, 1.00, 0.65, "BLOCK"),
}

ok = True
for name, (esc, nt, bf, tf, eb, et, ed) in cases.items():
    b, t = bis(bf), tds(tf)
    d = directive(esc, nt, b, t)
    match = (b, t, d) == (eb, et, ed)
    ok &= match
    print(f"{'PASS' if match else 'FAIL'}  {name}: BIS={b} TDS={t} -> {d}")

print("\nBoundary probes:")
print(f"  TDS exactly 0.35 -> {directive(False, False, 1.0, 0.35)} (expect PASS)")
print(f"  TDS exactly 0.55 -> {directive(False, False, 1.0, 0.55)} (expect RE-ANCHOR)")
print(f"  TDS 0.56         -> {directive(False, False, 1.0, 0.56)} (expect BLOCK)")
print(f"  BIS exactly 0.70 -> {directive(False, False, 0.70, 0.0)} (expect PASS)")
print(f"  BIS 0.69         -> {directive(False, False, 0.69, 0.0)} (expect NEEDS-PROVENANCE)")
print(f"  BIS 0.50 + TDS 0.60 -> {directive(False, False, 0.50, 0.60)} (expect BLOCK, precedence)")
print(f"  caps: 5 junk commits -> BIS {bis({'junk_commit': 5})} (expect 0.70, cap held)")
print(f"  caps: 6 oos files    -> TDS {tds({'oos_file': 6})} (expect 0.30, cap held)")
print("\nALL CASES PASS" if ok else "\nFAILURES PRESENT")
