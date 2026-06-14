# PR Warden

**Technical report (citable):** [doi.org/10.5281/zenodo.20673314](https://doi.org/10.5281/zenodo.20673314)

**Your AI did the work. Did it do the work you asked for?**

AI coding assistants are fast, tireless, and very good at building something *almost* like what you wanted. A pull request shows up, the tests pass, the code looks clean — and it quietly solves a different problem than the ticket asked for, or solves three tickets at once, or brings in a dependency nobody approved. Every light on the dashboard is green. The work still drifted.

PR Warden is a gate that catches that. It reads the pull request, reads the ticket it claims to serve, and answers one question: **does this PR do what its ticket says — and nothing else?** Then it gives exactly one of four answers:

- ✅ **PASS** — on-ticket, well-documented, merge away
- 📋 **NEEDS-PROVENANCE** — the work may be fine, but the paper trail isn't (junk commits, empty descriptions)
- 🧭 **RE-ANCHOR** — valid work that's wandered off the ticket; re-aim it or grow the ticket
- ⛔ **BLOCK** — wrong ticket, no ticket, or too far gone

And the part that makes it different from every AI review tool: **it isn't an AI.** Every verdict comes from fixed, published rules — simple checks anyone can read, with the math shown. Same input, same answer, every time. It runs for free as one of your repo's automatic checks (the "CI" — the row of green checkmarks and red X's GitHub stamps on every pull request): no API key, no subscription, no model anywhere in the loop. When it flags something, it tells you exactly which rule fired and why, like a referee who shows you the rulebook page.

## Try it in 60 seconds

1. **Click around:** open `demo/index.html` in your browser — the actual gate, running locally on your machine. Load a preset, hit Run, watch it decide.
2. **See it on a real PR:** it ran live on GitHub against a real pull request and real issue — verdict comment, scores, check mark, no human and no AI involved: [mrcord77/warden-test PR #2](https://github.com/mrcord77/warden-test/pull/2).
3. **Install it in one block:** add `uses: mrcord77/pr-warden@master` to a 12-line workflow file (full copy-paste block at the top of `action.yml`) and it gates every PR in your repo from then on.

**The bigger idea (the part worth stealing):** this gate is one *aiming* of a reusable pattern — a declared baseline, an incoming change, transparent scoring, four verdicts. Aim the same machine at agent commits and you get [CDLO](https://github.com/mrcord77/context-drift-ledger-operator), this gate's predecessor. Aim it at your own workflow using **`AIMING.md`**, the ten-step worksheet included here — with a filled example for a third domain to prove it's plug-and-play. The whole story, including the testing saga that shaped the method, is one read: **`PAPER.md`**.

---

# Under the hood

*Everything below is the engineering layer — the rules, the receipts, the file map. You don't need it to use the gate. It's here because trustworthy means checkable.*

*Packaging note: this operator folder follows Van Clief's Interpretable Context Methodology (ICM, arXiv:2603.16021) — ICM is the folder-as-architecture convention; the governance pattern inside it is this project's contribution.*

## Lineage
PR Warden is the second operator built on the CDLO discipline (github.com/mrcord77/context-drift-ledger-operator). CDLO's live adversarial testing produced one transferable finding: every defect traced to rule conditions written as *descriptions*, which different sessions interpreted differently — never to the arithmetic, which was perfect every run. PR Warden therefore writes **every condition as a boolean test from day one**, and its worked examples were generated *by* the model-free referee script rather than verified against it afterward.

## How to use it
**Zero-install demo:** open `demo/index.html` in any browser — the full gate running as ~150 lines of client-side JavaScript. Fill the ticket and PR fields yourself or load any of the five presets; every boolean test fires (or doesn't) live in the execution log. No AI, no server, no key: because the rules are boolean tests plus arithmetic, the demo isn't a recording of the gate — it *is* the gate. (One honest exception: escalation Trigger 2, the self-contradicting ticket, needs semantic reading and stays with the full operator.) Hostable as-is on GitHub Pages.

**Fastest path:** open `TRY_IT.md` — five ready-to-paste payloads, 60 seconds to a verdict. `sample_run/warden_dashboard.html` shows what a week of verdicts looks like before you run anything.

**Claude Code:** `cd` here, run `claude` (CLAUDE.md auto-loads the operator), paste a Ticket block + PR payload. Or generate the payload from a real PR: `python scripts/extract_pr_payload.py --repo owner/name --pr 87`.
**Chat:** paste `system_prompt.md` + `rules.md` + `reference/template_out.md` as message one, ticket + payload as message two.
**CI one-block install (reusable Action):** add a 12-line workflow with `uses: mrcord77/pr-warden@master` (full block at the top of `action.yml`) — nothing vendored, no API key; the engine runs from the action's own checkout. *Status: live-verified — ran on real GitHub infrastructure against a real PR and its linked issue, posted the full verdict comment, and set the check state correctly (BIS 0.80 / TDS 0.20 / PASS, every fired test matching the reference engine to the digit).*

**CI vendored install (verified logic):** `action/pr-warden.yml` runs the gate on every PR with **no AI and no API key** — `scripts/run_gate.py` is the full rules engine in plain Python (the third independent implementation, verified against the referee and the browser demo). The Action extracts the PR and its linked GitHub Issue (write "Closes #42" in the PR body; issue format in `reference/ticket_convention.md`), scores it, posts the verdict as a comment, applies the `drift:re-anchor` label when warranted, and fails the check on BLOCK or ESCALATION. Install = copy the folder, drop the yml into `.github/workflows/`.

## What's in this folder
| File | Job |
|---|---|
| `AIMING.md` | The re-targeting template — ten steps to aim this pattern at a new workflow |
| `rules.md` | Boolean-test tables: Baseline Integrity Score, Ticket-Drift Score, thresholds, precedence, escalations |
| `identity.md` | Scope, limits, decision philosophy |
| `examples.md` | Five verdicts — clean pass, provenance freeze, silent drift, wrong-ticket block, racing-agents escalation |
| `system_prompt.md` | The runtime pipeline |
| `config.md` | Every threshold and weight, tunable in one place |
| `scripts/verify_rules.py` | Model-free referee — recomputes all examples + 8 boundary probes as plain code |
| `scripts/extract_pr_payload.py` | Payload from any live PR + its linked GitHub Issue, human or `--json` format |
| `scripts/run_gate.py` | The complete rules engine in plain Python — deterministic CI scoring, no AI |
| `reference/ticket_convention.md` | How to write a GitHub Issue the gate can read (task lists + optional Paths line) |
| `action.yml` | Reusable composite Action — `uses: mrcord77/pr-warden@master`, one-block install |
| `action/pr-warden.yml` | Vendored-install workflow (copy-in alternative) |
| `TRY_IT.md` | Five paste-and-go test payloads, one per directive |
| `scripts/build_warden_dashboard.py` | Drift-history dashboard from the verdict log |
| `sample_run/` | Populated verdict log + rendered dashboard, openable before you run anything |
| `demo/index.html` | Interactive calculator demo — the rules engine in client-side JS, with presets |

## Verify without the AI
`python scripts/verify_rules.py` — all worked examples, threshold boundaries, precedence conflicts, and deduction caps, recomputed in plain Python. If the live operator and the referee ever disagree, the referee is right and the prompt gets tightened.

## What this gate does not measure
Not code correctness (CI's job), not code quality (review's job), not ticket wisdom (the team's job). It measures traceability and scope adherence between a change and its declared baseline — and it is honest that its weights are policy, not physics: fixed, written, identically applied, tunable in `config.md`.

STATUS: v0.1 — live-verified. All five worked examples were run in a live Claude Code session and matched the referee to the digit on the first pass — zero interpretation defects, against the four that CDLO's descriptive-condition rules required before converging. The boolean-test discipline is not a style preference; it is the measured difference between four defect cycles and none.
