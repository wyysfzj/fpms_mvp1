# PD-NEW-CUSTOMER-FEEDBACK-REVIEW-20260712-01

## Story Shape Classification

- `shared_file_density`: low; the three tasks edit distinct ownership files.
- `prereq_dependency_density`: high; source registration precedes audit, and audit precedes customer clarification.
- `be_fe_coupling`: read-only high; no product code is writable.
- `evidence_cost`: high; mixed file types and website provenance require source-specific evidence.
- `chosen_runbook`: `P0-prereq-heavy-story`

## Execution Order

| Wave | Task file | Owner | Exact closure | Dependency |
| --- | --- | --- | --- | --- |
| 1 | `tasks/postdemo/PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01.md` | Main thread | Register and ledger new customer sources | None |
| 2 | `tasks/reviews/PD-NEW-CUSTOMER-FEE-SOURCE-REAUDIT-20260712-01.md` | Reviewer/writer agent | Update the existing audit report | Wave 1 PASS |
| 3 | `tasks/postdemo/PD-FEE-GRANT-CUSTOMER-CLARIFICATION-REFRESH-20260712-01.md` | Customer-doc writer agent | Refresh the existing clarification document | Wave 2 PASS |

## Shared-File Decision

No two tasks share a writable source or target file. Website and customer-source inspection is read-only. Each task has independent evidence and gate validation. Product code, tests, databases, and customer source files remain read-only.
