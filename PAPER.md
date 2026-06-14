# One Gate, Aimed Twice: A Reusable Pattern for Deterministic AI Governance

**Andre Cordero — June 2026**
**Published technical report:** https://doi.org/10.5281/zenodo.20673314
**Repositories: github.com/mrcord77/context-drift-ledger-operator · github.com/mrcord77/pr-warden**

This paper describes a reusable governance pattern — a declared baseline, an incoming change, boolean-test scoring, exactly four verdicts, and a model-free referee — demonstrated through two working instantiations built and adversarially tested in the same week: CDLO, which gates AI-agent commits against a project's declared intent, and PR Warden, which gates pull requests against their tickets. The pattern's claim is not either tool. It is more modest and more checkable: in these two builds, most of the gate — the pipeline, the verdict structure, the referee, the testing discipline — transferred between problem domains untouched, roughly seventy percent of it. The rest split into two parts: a translation procedure that proved documentable as a worksheet, and an irreducible core of domain judgment that no template can decide for you, which the worksheet now instructs builders to record rather than guess at. Whether those proportions hold in other domains is an open question the worksheet exists to test. And, — observed across the two builds — writing rule conditions as boolean tests instead of natural-language descriptions removed the entire class of defect that live testing kept finding: the first gate, written descriptively, required repeated defect-fix cycles to converge; the second, written as tests from the start, converged immediately. Two builds is a pattern worth reporting, not a law; the claim is offered for others to break.

Both operators are packaged as ICM operator folders per Van Clief's Interpretable Context Methodology (arXiv:2603.16021), the folder-as-architecture convention this competition is built around. ICM governs the packaging — how context is structured and loaded; the governance pattern inside it — the scoring, verdicts, referee, and testing discipline — is this work's contribution.

## The problem nobody's tests are catching

AI-assisted software development has a failure mode that traditional quality gates were never designed to see. Tests catch broken code. Linters catch sloppy code. Security scanners catch vulnerable code. But none of them catch *competent code that is quietly building the wrong thing*.

Picture an AI coding agent that works through the night. Every commit is signed. Every test passes. The work is genuinely good. And it has spent six hours optimizing a delivery pipeline that nobody asked for, while the feature the project actually declared — the one written down as its purpose — sits untouched. Nothing is broken, so nothing flags. Multiply that by parallel agent sessions running simultaneously, and a project can drift so far from its declared intent that by the time a human notices, the codebase is a different product than the one that was planned.

This is not hypothetical. It is the characteristic failure of multi-agent and AI-assisted builds: not failures of quality, but accumulations of valid work off-axis. The drift compounds silently precisely because every individual change looks fine.

The Context-Drift Ledger Operator — CDLO — exists to catch that failure at the merge boundary, mechanically, on every change.

## What it is

CDLO is a governance gate built entirely from readable markdown files. There is no application to install and no framework to adopt. The folder itself is the operator: a system prompt that defines a strict pipeline, a rules file containing every scoring table, worked examples, and reference templates. Drop the folder into an AI coding environment, paste in two things — the project's declared intent and a proposed change — and the operator returns exactly one of four verdicts:

**AUTHORIZE EXECUTION.** The change is aligned and verifiable. Proceed.

**EXECUTION FREEZE.** The work may be on-target, but its provenance is not verifiable — missing signatures, missing timestamps, draft status without ownership. Nothing executes until the authority chain is repaired.

**MANDATORY LIFECYCLE PIVOT.** The most important verdict, and the reason the system exists. The work is valid, signed, and passing — and it is drifting from declared intent. The gate freezes forward motion until either the intent file is updated to include the new direction, or the work is re-anchored to the original objective. The drift gets reconciled instead of compounding.

**INTEGRATION HALT.** The change is decoupled beyond a recoverable boundary, or the context layer itself is broken.

The operator never asks the user what to do. Uncertainty routes to a freeze, a halt, or an escalation — never back to the human as a question. That is the difference between an operator and a chatbot: it decides, then routes the work.

## How the scoring works

Every verdict is arithmetic, not vibes. Two scores are computed from fixed tables.

The Context Confidence Interval starts at 1.00 and takes deductions for verifiability failures: 0.30 for a draft document without an owner signature, 0.30 for a missing signature entirely, 0.25 for a missing relationship linkage between entities, 0.20 for an asset outside declared scope, 0.15 for a missing timestamp. Fall below the 0.70 floor and execution freezes regardless of how aligned the work is.

The Context-Drift Score starts at 0.00 and climbs with each drift finding: 0.15 if the change references no declared objective, 0.15 if it maps to no open work item, 0.10 for each file touched outside declared scope, 0.10 for each undeclared dependency, 0.20 for modifying an archived entity, 0.15 for an unauthorized author. Up to 0.35 is locked alignment. Between 0.35 and 0.55 triggers the pivot. Above 0.55 is a halt.

An honest caveat is written directly into the rules: these weights are policy defaults, not measured quantities. There is no empirical reason a missing signature costs 0.30 rather than 0.25. What matters is that the values are fixed, written down, applied identically to every payload, and tunable in one configuration file rather than improvised per decision. The scores are reproducible policy outputs — auditable and consistent — not objective measurements of project health. Similarly, the Context Confidence Interval is a constructed integrity score, not a confidence interval in the statistical sense.

Two escalation triggers sit above the entire pipeline. The Coherent Decoy fires when multiple agent sources submit changes that agree with byte-level precision while all of them skip identity verification — the signature of an uncoordinated consensus trying to manufacture authority. Agreement is not verification; three agents saying the same thing is one claim repeated three times. The Verified Contradiction fires when two properly signed sources make incompatible claims about each other. The operator is explicitly forbidden from picking a side, however plausible one looks — two verified sources in contradiction means the context layer itself is broken, and the only honest output is a locked gate with the exact coordinates of the conflict.

## The referee you don't have to trust

The deepest problem in AI governance is recursive: if an AI system grades work, who grades the grader? Most AI evaluation today is a model checking a model — confidence scores generated by the same kind of system being evaluated.

CDLO's answer is a script. Because every score is table arithmetic, the entire scoring system is reimplemented in roughly eighty lines of plain Python with no AI anywhere in it. Run the verification script and it recomputes every worked example plus six boundary probes — exact thresholds, precedence conflicts — and the numbers must match what the live operator produces. When they were compared on the same payload, the AI operator and the model-free referee agreed to the digit: confidence 0.80, drift 0.50, mandatory pivot. That agreement — not the model's confidence in itself — is what makes a verdict trustworthy.

## What testing found, four times

The system was adversarially tested in live sessions before release, and the testing caught four real defects that careful specification had not prevented. Every one is preserved in the project's record, because together they form the strongest argument for the methodology — and the most useful finding of the entire build.

The first defect made the system's core purpose unreachable. As originally written, the identity rule treated a well-formed ID that simply wasn't declared in the intent file the same as a malformed or conflicting ID — both triggered an immediate halt. The first live test exposed the consequence: every piece of drifting work halted at the integrity check before the drift scoring could ever run. The pivot verdict — the entire reason the system exists — was dead code. The rule was split: integrity failures still halt, but undeclared-yet-valid entities route to drift scoring, where they belong.

The second defect was a rule two sessions read two different ways. The relationship-linkage deduction — a quarter-point for an entity with no declared link to any other — is ambiguous when a payload contains only one entity. One session read it as not applicable, since there was nothing to link to. Another session read it as fired, since no linkage existed. Both readings were defensible, which meant the rule was not deterministic — the one sin this operator is not allowed.

The third defect was the most instructive: the fix for the second defect created it. The disambiguation — "applies when the payload contains two or more entities and an entity has no declared relationship to any other" — resolved the single-entity case but silently flipped a different one: two files committed together with no explicit relationship line between them. Under the new wording, a session correctly fired the deduction on the system's own flagship example, dropping a drift case below the confidence floor and turning its pivot into a freeze. The repair defined linkage operationally: files in the same commit are implicitly linked — the commit is their relationship — and the deduction fires only for an entity isolated from every other.

The fourth defect was a double-count. The tables carry two signature deductions — one for a draft document without an owner signature, one for a modification missing a signature entirely — and nothing said whether a single missing signature could trigger both. One session stacked them, charging the same absence twice. The repair made the two mutually exclusive, each with an explicit boolean test for when it fires.

Four defects, four fixes, and after the last one a full verification run landed every number, every directive, and every cited rule exactly as specified — the first perfect suite. But the pattern across all four matters more than any of them. Not one defect was in the arithmetic: the scores summed correctly every single time. Every defect was in condition interpretation — a rule written as a description ("missing relationship linkage," "missing signature entirely") that a human reads one way and different sessions read different ways. Descriptions get read; tests get executed. Each fix converted a description into a boolean test, and the ambiguity vanished.

That is a finding with reach beyond this project: deterministic governance built on a language model does not fail at the math. It fails at the natural-language conditions feeding the math — and the mitigation is to specify those conditions the way you would specify them to a compiler. None of the four defects could have been found by the system checking itself, and the verification script — which validates the arithmetic — caught none of them either, because the arithmetic was never wrong. Only independent, repeated live runs could expose interpretation drift. A gate that governs other people's drift should survive its own gate. This one eventually did — and the discipline that got it there is the same one the operator enforces: never trust work that has only been graded by the system that produced it.

## Proven on a real repository

Worked examples are easy to rig, so the repository includes a run against a real published project: beacon-hunter, an open-source network security tool for detecting structured command-and-control beaconing, released under AGPL-3.0 and archived on Zenodo. The included git bridge generated the payload directly from the repository's actual commit history — author, timestamp, message, files touched, scope checks, all pulled from real git data. The intent file was drafted strictly from the project's own public README. The gate evaluated the repository's actual head commit, a DOI-archival change, and returned an authorization with full traceability: confidence 1.00, drift 0.00, every line justified. Anyone can clone the repository and reproduce the run. The gate is as accountable for its approvals as for its halts.

## What it deliberately does not do

CDLO measures consistency between a change and its declared intent — documentation discipline, scope adherence, provenance. It does not measure semantic correctness. A change could reference all the right identifiers while implementing something entirely different underneath, and this gate would pass it. Whether the code works, the architecture is sound, or the implementation matches its claimed behavior is the job of tests, continuous integration, and human review. CDLO sits beside those gates, never instead of them.

It is also not ungameable. Anyone who knows the deduction tables can optimize the paperwork instead of the engineering — true of every governance system ever built. The mitigations are twofold: gaming this gate at least forces the drift to be documented, which is half the battle, and the Coherent Decoy trigger catches the most common automated form, multiple agents polishing identical paperwork in lockstep.

And a pivot or halt is a flag with coordinates, not a final ruling. The human decides whether the intent should change or the work should. The gate's job is to force that decision to happen now, while the drift is one commit deep, instead of six months later when it is the architecture.

## The second aiming: same machine, new target

PR Warden is the proof that the pattern travels. Its baseline is a ticket instead of an intent file — chosen deliberately, because CDLO's honest adoption weakness was asking users to create a document that doesn't exist in their lives, and tickets already do. Its change unit is a pull request. Its four verdicts map onto GitHub check states: pass, needs-provenance, re-anchor, block. Its escalations are the same two anomalies in new clothes: multiple agents racing one ticket with identical submissions, and a ticket whose own acceptance criteria contradict each other. The translation took about a day. The pipeline order, precedence chain, referee skeleton, configuration pattern, persistence layer, and testing discipline transferred without modification.

What did not transfer was rewritten under the lesson the first gate paid for: every condition as a boolean test from the first line. The measured result: PR Warden's five worked examples, run in a live session, matched the model-free referee to the digit on the first pass — zero interpretation defects, against the four CDLO required to converge. The same rules were then implemented a third time, as a browser demo in plain JavaScript, and a fourth time as a Python engine with CI exit codes; all implementations agree to the digit. A rule set that four independent implementations compute identically is about as verified as a rule set gets — and none of those implementations contains a model, which means the gate now runs in continuous integration deterministic, free, and with no API key at all.

## The thirty percent, as a worksheet

If most of a gate transfers, the part that doesn't is the product — and as much of it as possible should be procedure rather than folklore. Both repositories now ship AIMING.md: a ten-step template that walks a workflow from "what document declares intent here?" through verdict mapping, boolean-test authoring with explicit skip semantics, the two escalation anomalies, policy-weight declaration, referee porting, referee-generated examples, and the live-test loop — with convergence expectations stated from the measured data. The template closes with a fully filled worksheet for a third domain neither gate serves: a change-order gate for client scope creep, where the baseline is a signed statement of work and the change unit is an inbound client request. The worksheet specifies its verdicts, integrity tests, drift tests, and escalations in roughly a page. The estimated cost of building it, using the template against the existing reference implementations, is two working sessions. That is the pattern's claim made falsifiable: anyone can take the worksheet and check the estimate. Early independent execution — a different model, no shared context, given only the repositories and asked to aim the pattern at unfamiliar domains — has begun: it produced working gate specifications, exposed real gaps in the template that were then fixed, and on re-execution confirmed the fixes while finding no new structural gaps, leaving only domain-policy judgment as the residue. This is a convergence signal, not a proof; serious verification means many executions across many domains by people as well as models, and that work is open. What matters is the loop itself: the template is subject to the same discipline as the gates it describes — tested by something that didn't write it, patched where it fails, and never graded by its own author alone.

## The larger pattern

CDLO is a small system, built fast, around one idea: in AI-assisted development, the scarce resource is not capability but verifiability. Models can produce unlimited competent-looking work. The bottleneck is knowing — mechanically, reproducibly, without trusting the producer — whether that work is still pointed at the declared target.

The design choices follow from that one idea. Decision logic in readable markdown, so the brain is auditable. Fixed scoring tables, so verdicts are reproducible. A model-free referee, so the grader can be graded. Persistent verdict logs and a drift-trend dashboard, so a project's trajectory toward or away from its intent is visible before it crosses the halt line — because a single drift score is a data point, but a trend is a story. And a documented record of the system's own failures, because a governance tool that hides its defects has no business governing anything.

The pattern generalizes. Every layer of AI autonomy added to a workflow adds a layer where silent drift can accumulate. The answer is not more capable models grading themselves harder. It is small, boring, deterministic gates — written down, testable by hand, and honest about their limits — standing at every boundary where work crosses from proposed to executed.

That is what these repositories are: one pattern, aimed twice, tested until it broke, fixed until it held, published with its receipts — and shipped with the worksheet for aiming it a third time.
