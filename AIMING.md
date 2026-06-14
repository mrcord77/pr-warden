# AIMING THE GATE — a re-targeting template

CDLO and PR Warden are the same machine pointed at two different problems. About 70% of a gate transfers untouched between targets: the pipeline order, the four-verdict structure, the precedence chain, the referee script skeleton, the config pattern, the persistence and dashboard layers, the testing discipline. The other 30% is *aiming* — mapping your domain onto the pattern. This file is that 30%, as a worksheet — a starting scaffold, not a universal recipe. It was extracted from two builds and early independent runs, which means it encodes what worked in those domains; yours will push back somewhere, and the worksheet's job is to make sure the pushback lands in a recorded decision instead of a silent guess. Work the ten steps with the existing repos as reference implementations, and expect a first-pass spec that your own live testing then has to earn.

## The pattern, in one sentence
**A declared baseline + an incoming change + boolean-test scoring + exactly one of four verdicts + a model-free referee that can recompute every score.**

---

## The ten steps

### 1. Name the baseline
What document declares intent in your domain? It must either already exist (a ticket, a contract, a spec, a style guide) or be cheap to create. *If users must invent a new document before the gate can judge anything, adoption dies — prefer baselines people already have.*
- CDLO: the intent file (invented — its adoption weakness, learned honestly)
- PR Warden: the ticket (pre-exists — chosen because of that lesson)

**And write the baseline's convention doc.** Baselines vary wildly inside any domain (contracts alone span fixed-fee, hourly, milestone, retainer). Your tests need anchors, so define the required structure the way PR Warden's `reference/ticket_convention.md` does for tickets: which fields, which markers, what's optional, what absence means. A baseline without a declared shape produces tests without mechanical footing. *(Gap found by independent template verification — see Verification status below.)*

### 2. Name the change unit
What arrives to be judged, and how does it arrive? One unit per run.
- CDLO: a commit / change payload. PR Warden: a pull request.

### 2b. Define the payload schema before writing any test
Boolean tests operate on *extracted fields*, not raw documents. "Billed service appears in the contract's deliverables" is only boolean after something has produced a normalized list of billed services and a normalized list of deliverables. So specify the extraction contract first — the exact JSON/fields a payload must carry (both reference gates do this: PR Warden's `run_gate.py` docstring schema, fed by `extract_pr_payload.py`). The rule of thumb: **if a test needs a parser, the parser's output format is part of the spec.** Matching rules must be mechanical too — substring, exact ID, normalized-name equality — and stated in the test. *(Gap found by independent verification: a tester had to invent a matching rule the template never authorized.)*

### 3. Map the four verdicts to domain actions
The verdict names can change; the four-slot structure should not — it has survived two domains intact. Define what each *does*:
| Slot | Meaning | CDLO | PR Warden | Yours |
|---|---|---|---|---|
| Green | aligned + verifiable | AUTHORIZE EXECUTION | PASS → success check | |
| Provenance | possibly aligned, not verifiable | EXECUTION FREEZE | NEEDS-PROVENANCE → comment | |
| Drift | valid work, off-baseline | MANDATORY LIFECYCLE PIVOT | RE-ANCHOR → label + comment | |
| Stop | beyond recoverable / no baseline | INTEGRATION HALT | BLOCK → failed check | |

### 4. Write the integrity tests (your BIS/CCI)
"Is this baseline+change pair *verifiable*, independent of alignment?" 4–6 deductions. **Every condition must be a boolean test, not a description** — string presence, length threshold, field absent, exact label match. State mutual exclusions explicitly (one fact never counted twice).
> This is the rule with teeth: across both gates, every live-testing defect (five total) traced to a condition written as a description that different sessions read differently. Zero traced to arithmetic. Descriptions get read; tests get executed.

### 5. Write the drift tests (your TDS/CDS)
"Does the change serve the baseline, and nothing else?" 4–6 additions with per-item caps. Define SKIP semantics for every test whose data may be absent: **a skipped test is skipped, never inferred** ("ticket declares no paths → scope test SKIPPED" — the gate never guesses scope).

### 6. Define the two escalation anomalies
Both have translated cleanly twice; find your domain's version:
- **Suspicious agreement** (CDLO: coherent decoy; Warden: agents racing one ticket): multiple sources agreeing exactly while skipping verification. Agreement is not verification.
- **Contradictory baseline** (CDLO: verified contradiction; Warden: self-contradicting ticket): the baseline disagrees with itself. The gate never picks a side — a broken baseline can't adjudicate anything. Always escalate.

Two cautions, both paid for: contradiction detection is inherently **semantic** — mark it as the one test that stays with the full operator and is excluded from your deterministic engine, as both reference gates do. And never write **compound tests** ("outside term OR duplicate period") with SKIP applying to only half; split them into two tests — condition conflation was the very first defect in the pattern's history.

### 7. Set thresholds and weights — and call them policy
Start from the inherited defaults (green ≤ 0.35, drift band 0.35–0.55, stop > 0.55, integrity floor 0.70) and tune. Put every number in `config.md`. State in writing that the weights are **policy defaults, not measurements** — fixed, written, identically applied, tunable in one place, never improvised per decision.

### 8. Port the referee
Copy `scripts/verify_rules.py`, swap in your tables. The referee is non-negotiable: it is what makes the gate's verdicts checkable without trusting the model. If a rule can't be implemented in the referee, it isn't a boolean test yet — go back to step 4.

### 9. Generate the examples FROM the referee
Run the referee first; write the worked examples from its output, never the reverse. One example per verdict slot plus each escalation. (PR Warden's examples were referee-generated; the referee caught a hand-written label error during the build.)

### 10. Run the live-test loop until convergence
Fresh session, paste every example, compare to the referee to the digit. Expect interpretation defects; each fix converts a description into a test. Convergence data so far: descriptive conditions took **4 defect cycles** (CDLO); boolean-from-day-one took **0** (PR Warden, first pass 5/5). Keep your defect log — it is the trust artifact.

---

## Worked third aiming (filled worksheet, unbuilt): the Change-Order Gate

Domain: freelance/agency scope creep — out-of-scope client requests, a documented, expensive, daily problem.

1. **Baseline:** the signed SOW/contract (pre-exists ✓)
2. **Change unit:** one inbound client request (an email or message)
3. **Verdicts:** IN-SCOPE (do it) / CLARIFY (request is too vague to score — drafted clarifying question) / CHANGE-ORDER (out of scope — drafted change-order email with the SOW section cited) / DECLINE (conflicts with an exclusion clause — drafted polite decline)
4. **Integrity tests:** SOW has no deliverables section (−0.30) · request references no project identifiable in the SOW (−0.25) · SOW unsigned/undated (−0.20) · request body < 20 chars (−0.15). Floor → CLARIFY.
5. **Drift tests:** request names a deliverable absent from the SOW's deliverable list (+0.20) · request asks to "add/also/extra/new" against a fixed-scope clause (+0.15) · revision request exceeding the SOW's stated revision count for that deliverable (+0.15 each, cap +0.30) · request names a service in the SOW's exclusions (+0.25)
6. **Escalations:** two stakeholders from the same client issuing contradictory instructions (never pick a side — escalate to the client's named decision-maker) · a request claiming "as we agreed" with no matching SOW or logged change-order (agreement-claim without verification)
7. **Thresholds:** inherited defaults; tune after live use
8–10. Same referee skeleton, referee-generated examples, live-loop to convergence.

Estimated aiming cost, using this template: one working session for steps 1–9, one live-test session for step 10. That is the product: not the gate — the aiming.

---

## What this pattern can and cannot gate
The pattern requires three things: a baseline that exists as **text**, changes that arrive as **discrete units**, and drift that leaves **mechanical fingerprints** — strings, paths, counts, presence/absence. Inside that boundary (document-governed change streams: commits vs. intent, PRs vs. tickets, invoices vs. contracts, requests vs. SOWs) it transfers. Outside it — "does this essay match our brand voice?" — there is no boolean test, and forcing the pattern there reintroduces exactly the model-judgment drift it exists to eliminate. Also **state the gate's direction**: a gate detects violations in one direction (overbilling, out-of-scope work) and deliberately permits the other (underbilling, smaller-than-allowed changes). Say which, or testers will guess.

## The domain policy register — what the template cannot decide for you
Independent verification rounds revealed a residue the template can name but never resolve: **domain vocabulary**. Every aiming forces choices like — what are this domain's scope dimensions (components? paths? deliverables?), what evidence types count, whether actors match by role or by name, where risk/severity values come from, and how strict the baseline convention may be when real documents are messy. These are not template defects; they are the irreducible aiming judgment — the actual expertise an aiming engagement sells. The procedure: as you fill the worksheet, keep a **domain policy register** — one line per such choice, with the option taken and why. This converts unauthorized judgment calls into authorized, recorded decisions, and the register becomes the first artifact a domain expert reviews.

## Verification status
This template has been exercised once by an **independent model with no shared context**, which was pointed at this repo and asked to aim the pattern at a fourth domain (an invoice-vs-contract gate) while keeping a friction log. Result: a complete, internally consistent gate skeleton — referee verified independently, SKIP semantics and caps used correctly, verdicts referee-generated — plus eight friction entries, three of which were real template gaps now patched above (baseline convention doc, payload-schema-first, semantic/compound test cautions). A second independent round (a different domain: deployment requests vs. release runbooks) confirmed the patches, surfaced no new structural gaps, and left only domain-policy choices — now handled by the domain policy register above. Honest weight: this is early, small-n verification — a signal that the template converges, not a demonstration that it's done. Live-test loops, more domains, and human (not just model) executions remain open, and any of them may find what these rounds didn't.
