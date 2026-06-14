# TICKET CONVENTION — GitHub Issues as the baseline

The gate needs a machine-readable baseline. For GitHub Issues, the convention is four optional structures inside an ordinary issue — nothing exotic, all of it readable by humans first:

```markdown
Add CSV export to the reports page so analysts can pull data into spreadsheets.

## Acceptance criteria
- [ ] export button on /reports
- [ ] CSV matches table columns

Paths: src/reports/
```

**Mapping (what the extractor reads):**
- **Ticket ID** = `#<issue number>` (e.g. `#42`) — referenced from the PR via "Closes #42" / "Fixes #42" in the PR body, or passed with `--issue 42`.
- **Description** = the issue body minus the structures below.
- **Acceptance criteria** = the issue's task-list items (`- [ ]` / `- [x]`), in order. Criterion (1) is the first task item.
- **Paths** = a line beginning `Paths:` — comma-separated path prefixes. Absent → the out-of-scope test is SKIPPED (scope is never inferred).
- **Assignee** = the issue's assignee field. Absent → the author≠assignee test is SKIPPED.
- **Status** = open/closed from the API.

**What this buys:** zero new tools, zero new accounts. Teams already writing issues with task lists are already 90% compliant; adding a `Paths:` line is the only new habit, and it's optional. Jira/Linear adapters follow the same shape — only the fetch step differs.
