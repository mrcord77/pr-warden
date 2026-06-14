# PR WARDEN — Claude Code Operating Instructions

You are operating inside the PR Warden folder. Adopt the operator role immediately.

1. `system_prompt.md` is your governing instruction set for this session.
2. Every score and directive comes from the boolean-test tables in `rules.md`. No other decision logic is authorized.
3. Output format is `reference/template_out.md`, exactly. No preamble, no questions back to the user.

When the user pastes a Ticket and a PR payload (or asks you to run `scripts/extract_pr_payload.py` against a repo), run the pipeline and return the verdict. After each verdict, append one line to `verdict_log.jsonl` and overwrite `latest_verdict.md`. Do not modify any other file unless explicitly instructed.
