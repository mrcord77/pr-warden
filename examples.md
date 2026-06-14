# EXAMPLE VERDICTS
Four runs, one per directive. Every number below was computed by `scripts/verify_rules.py` BEFORE being written here — the referee generated the examples, not the other way around.

---
## CASE 1: CLEAN PASS
**Ticket** `APP-310` — "Add CSV export to reports page." Criteria: (1) export button on /reports, (2) CSV matches table columns. Paths: `src/reports/`. Assignee: @dev_a.
**PR** #87 by @dev_a — title "APP-310: CSV export for reports", body addresses both criteria by number, commits: `APP-310: add export button`, `APP-310: csv serializer`. Files: `src/reports/Export.tsx`, `src/reports/csv.ts`. No new deps.
**Run:** No escalation. BIS 1.00 (no test fires). TDS 0.00 — D1 ticket ID present in title (NOT FIRED), D2 both criteria addressed (NOT FIRED), D3 both files inside `src/reports/` (NOT FIRED), D4 no deps, D5 no foreign IDs, D6 author = assignee.
**Directive:** `PASS` → success check.

---
## CASE 2: NEEDS-PROVENANCE (aligned work, unverifiable paper trail)
**Ticket** `APP-311` — full description, criteria, paths `src/auth/`. Assignee @dev_b.
**PR** #91 by @dev_b — title "APP-311: session fix", body: "fixes it" (8 chars → B2 FIRED −0.20). Commits: `wip`, `fix`, `more` (3 × B3 −0.10 = −0.30, at cap). Files inside `src/auth/`.
**Run:** BIS 1.00 − 0.20 − 0.30 = **0.50** < 0.70 floor. TDS **0.10** — D2 fires (the criterion is neither quoted, checkboxed, nor referenced by number in an 8-character body); all other drift tests clean.
**Directive:** `NEEDS-PROVENANCE` → neutral check + comment requesting a real PR body and squashed/labeled commits. **Why it matters:** the work is on-ticket; a drift-only gate passes it. But three junk commits and an 8-character body make the change unauditable six months from now — the gate prices that in before merge, when it costs minutes instead of archaeology.

---
## CASE 3 (EDGE): THE SILENT DRIFT
**Ticket** `APP-312` — "Optimize report query performance." Criteria: (1) p95 under 800ms. Paths: `src/reports/`. Assignee @agent_4.
**PR** #95 by @agent_4 — title "Performance improvements", body describes caching work, never cites APP-312 (D1 FIRED +0.15). Files: `src/reports/query.ts` (in scope), `infra/cache/layer.ts`, `infra/cache/config.ts` (2 × D3 +0.10 = +0.20). Adds dependency `redis` — appears nowhere in ticket (D4 +0.10). Criterion (1) addressed in body (D2 NOT FIRED).
**Run:** BIS 1.00. TDS = 0.15 + 0.20 + 0.10 = **0.45** — in the (0.35, 0.55] band.
**Directive:** `RE-ANCHOR` → neutral check, label `drift:re-anchor`, comment: work is valid and possibly excellent — but half of it lives outside the ticket's declared scope with an undeclared infrastructure dependency. Either the ticket grows to own the cache layer, or the cache work moves to its own ticket. **The edge:** nothing here is broken, and that's the point — this is how agent-assisted repos rot, one competent off-axis PR at a time.

---
## CASE 4: BLOCK (the wrong-ticket PR)
**Ticket** `APP-313` — "Update onboarding email copy." Criteria: (1) new copy per attached doc. Paths: `src/email/`. Assignee @dev_c.
**PR** #102 by @agent_7 (D6 FIRED, +0.10) — title "misc fixes", no APP-313 anywhere (D1 +0.15). Commits reference `APP-309` and `APP-314` (2 × D5 +0.15 = +0.30). Criterion (1) unaddressed (D2 +0.10).
**Run:** BIS 1.00. TDS = 0.15 + 0.30 + 0.10 + 0.10 = **0.65** > 0.55.
**Directive:** `BLOCK` → failure check. A PR carrying two other tickets' work, authored by a non-assignee, addressing none of its own ticket's criteria is not a merge candidate under any reading.

---
## CASE 5 (ESCALATION): AGENTS RACING ONE TICKET
Two open PRs — #103 by @agent_8 and #104 by @agent_9 — both titled "APP-315: implement webhook retry", identical changed-file lists.
**Run:** Trigger 1 boolean test satisfied (same ticket ID + identical title + identical file list). No scoring performed.
**Directive:** `ESCALATION: COORDINATED DUPLICATE SUBMISSION — HUMAN REVIEW REQUIRED`, PRs #103/#104 and both authors listed. Merging either without review compounds the collision; two agents racing one ticket is a fleet-coordination failure, not a code problem.
