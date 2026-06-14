# TRY IT — 60 seconds to a verdict

Open this folder in Claude Code (`cd` here, run `claude` — CLAUDE.md loads the operator), or paste `system_prompt.md` + `rules.md` + `reference/template_out.md` into a fresh chat. Then paste any block below. Expected results are exact — same input, same numbers, every run.

## Test 1 → `PASS` (BIS 1.00, TDS 0.00)
```
Ticket APP-310 — "Add CSV export to reports page."
Criteria: (1) export button on /reports, (2) CSV matches table columns.
Paths: src/reports/. Assignee: @dev_a. Status: Open.

PR payload:
PR #87 | author @dev_a | draft: false
title: "APP-310: CSV export for reports"
body (210 chars): "Implements APP-310. Criterion (1): export button added to /reports toolbar. Criterion (2): CSV columns generated from the table schema so they always match."
commits:
  a1b2c3d: "APP-310: add export button"
  e4f5a6b: "APP-310: csv serializer"
files:
  src/reports/Export.tsx
  src/reports/csv.ts
```

## Test 2 → `NEEDS-PROVENANCE` (BIS 0.50, TDS 0.10 — D2 fires: an 8-character body addresses no criterion)
```
Ticket APP-311 — "Fix session timeout on auth refresh."
Criteria: (1) session persists through token refresh.
Paths: src/auth/. Assignee: @dev_b. Status: Open.

PR payload:
PR #91 | author @dev_b | draft: false
title: "APP-311: session fix"
body (8 chars): "fixes it"
commits:
  b1c2d3e: "wip"
  f4a5b6c: "fix"
  d7e8f9a: "more"
files:
  src/auth/session.ts
```

## Test 3 → `RE-ANCHOR` (BIS 1.00, TDS 0.45)
```
Ticket APP-312 — "Optimize report query performance."
Criteria: (1) p95 under 800ms.
Paths: src/reports/. Assignee: @agent_4. Status: Open.

PR payload:
PR #95 | author @agent_4 | draft: false
title: "Performance improvements"
body (180 chars): "Adds a caching layer for report queries. p95 measured at 410ms after warm cache, satisfying the sub-800ms criterion (1). Cache invalidation on report schema change."
commits:
  c1d2e3f: "add cache layer"
  a4b5c6d: "wire cache into query path"
files:
  src/reports/query.ts
  infra/cache/layer.ts
  infra/cache/config.ts
  package.json [dependency manifest] (adds: redis)
```

## Test 4 → `BLOCK` (BIS 1.00, TDS 0.65)
```
Ticket APP-313 — "Update onboarding email copy."
Criteria: (1) new copy per attached doc.
Paths: src/email/. Assignee: @dev_c. Status: Open.

PR payload:
PR #102 | author @agent_7 | draft: false
title: "misc fixes"
body (120 chars): "Cleanup pass: resolves the lingering retry issue from APP-309 and starts the APP-314 refactor while I was in the area."
commits:
  e1f2a3b: "APP-309: retry backoff"
  c4d5e6f: "APP-314: extract mailer interface"
files:
  src/email/mailer.ts
  src/email/retry.ts
```

## Test 5 → `ESCALATION: COORDINATED DUPLICATE SUBMISSION — HUMAN REVIEW REQUIRED`
```
Ticket APP-315 — "Implement webhook retry." Paths: src/webhooks/. Assignee: @engineering_lead. Status: Open.

PR payload (two open PRs against this ticket):
PR #103 | author @agent_8 | title: "APP-315: implement webhook retry"
files: src/webhooks/retry.ts, src/webhooks/queue.ts
---
PR #104 | author @agent_9 | title: "APP-315: implement webhook retry"
files: src/webhooks/retry.ts, src/webhooks/queue.ts
```

## Then verify without the AI
```
python scripts/verify_rules.py
```
Recomputes every case plus eight boundary probes (exact thresholds, precedence conflicts, deduction caps) in plain Python. Operator and referee must match to the digit.
