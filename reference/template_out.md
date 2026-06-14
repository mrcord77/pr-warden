# PR WARDEN VERDICT
[PR-WARDEN SPEC-v0.1]

## 1. AUDIT METRICS
* **Timestamp:** [ISO 8601]
* **PR:** [number/id] → **Ticket:** [ticket ID]
* **Baseline Integrity Score (BIS):** [0.00–1.00] (floor: 0.70)
* **Ticket-Drift Score (TDS):** [0.00–1.00] (re-anchor: 0.35, block: 0.55)

## 2. DIRECTIVE
```
[PASS / NEEDS-PROVENANCE / RE-ANCHOR / BLOCK / escalation string]
```
**GitHub check state:** [success / neutral + comment + label / failure]

## 3. EXECUTION LOG
* **Reasoning Path:** [Every boolean test from rules.md evaluated in order — FIRED or NOT FIRED with the input fact that decided it, running totals for BIS and TDS, threshold comparison, precedence resolution. Mechanical steps only.]
* **Action:** [exact check state + any label/comment to post]
