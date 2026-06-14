# CONFIG — gate tuning
Operator and `scripts/verify_rules.py` both read this file. Defaults apply if absent.

## Thresholds
| key | value |
|---|---|
| reanchor_threshold | 0.35 |
| block_threshold | 0.55 |
| bis_floor | 0.70 |

## BIS deductions
| key | value |
|---|---|
| empty_ticket | 0.30 |
| thin_pr_body | 0.20 |
| junk_commit | 0.10 |
| junk_commit_cap | 0.30 |
| closed_ticket | 0.20 |
| draft_pr | 0.15 |

## TDS additions
| key | value |
|---|---|
| no_ticket_ref | 0.15 |
| unaddressed_criterion | 0.10 |
| unaddressed_criterion_cap | 0.30 |
| oos_file | 0.10 |
| oos_file_cap | 0.30 |
| undeclared_dep | 0.10 |
| undeclared_dep_cap | 0.20 |
| foreign_ticket_commit | 0.15 |
| foreign_ticket_cap | 0.30 |
| author_not_assignee | 0.10 |
