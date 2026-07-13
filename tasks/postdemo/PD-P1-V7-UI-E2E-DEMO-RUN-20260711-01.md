# PD-P1-V7-UI-E2E-DEMO-RUN-20260711-01

Status: BLOCKED
Executor role: Demo Operator / UI E2E Tester

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Execute the approved V7 UI E2E demo against one fresh isolated SQLite environment, following
`docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md`, and record every attempted
checkpoint with its purpose, exact input fields/values, three-second pre-submit delay, expected and
observed UI result, legal-state observation, document/work-package state, fee-node state and amount.

## Explicit Non-Closure

Do not modify product code, schema, seed, tests, V6/V7 design documents, permissions, or shared
databases. Do not use route mocks, direct database writes, historical fixtures, the V6 helper, or
unapproved enrichment to bypass a stop condition. Do not claim READY when V7-13 remains BLOCKED.

## Dependencies

- `docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md`
- Tasks 1–4 in `tasks/batches/PD-P1-V7-DEMO-DOCS-20260711-01.md`: PASS

## Remaining Follow-Up Task IDs

- V7-safe application-fee/format-letter/annuity enrichment and cleanup mechanism: required if
  V7-13 is to move from BLOCKED to PASS; not implemented by this task.

## Allowed Files

- `tasks/postdemo/PD-P1-V7-UI-E2E-DEMO-RUN-20260711-01.md`
- `artifacts/PD-P1-V7-UI-E2E-DEMO-RUN-20260711-01/**`

## External Runtime Scope

- One fresh `/tmp/fpms_p1_v7_<RUN_ID>.db` SQLite database.
- One fresh `/tmp/fpms_p1_v7_storage_<RUN_ID>` directory.
- Local backend `127.0.0.1:8077` and frontend `127.0.0.1:5177` only.
- V7 facts created through visible UI or the Runbook's verified public UI/API behavior only.

## Verification Commands

- Lint: `git diff --check -- tasks/postdemo/PD-P1-V7-UI-E2E-DEMO-RUN-20260711-01.md artifacts/PD-P1-V7-UI-E2E-DEMO-RUN-20260711-01/run-record.md`
- Structure: assert `run-record.md` contains `V7-01` through `V7-14` and, for every attempted step,
  purpose, fields/values, three-second delay, expected result, observed result, legal state,
  document/work-package state, fee state/amount, and evidence.
- V6 freeze: exact three protected paths remain clean.
- Evidence validation and task gate are required only for PASS. BLOCKED preserves available evidence
  and records the exact stop condition.

## Evidence Path

- `artifacts/PD-P1-V7-UI-E2E-DEMO-RUN-20260711-01/**`

## Done Definition

Every safely reachable V7 checkpoint is executed and visibly observed on the isolated environment;
each submission waits three seconds after input; all state/fee observations are evidence-backed;
any Runbook stop condition is obeyed without bypass; the final status distinguishes task execution
from overall demo READY.
