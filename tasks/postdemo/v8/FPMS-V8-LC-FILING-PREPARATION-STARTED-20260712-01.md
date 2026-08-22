# FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `10. Wave 2B — one lifecycle event per task`
Catalog ordinal: `19`
Executor role: Backend Developer / worker

## Implementation Handoff — 2026-07-14

- Exact task-owned RED failed because the registry did not yet expose
  `FILING_PREPARATION_STARTED`; the minimum task-owned rule and test now make the exact
  target GREEN.
- The pre-GRANT RED unexpectedly triggered repository autouse Alembic/SQLite setup. The
  serialization incident is recorded in task-local evidence; all later pytest stopped
  until the controller issued an explicit GREEN `GRANT`.
- Task-scoped lint and the granted exact GREEN have passed. Final PASS remains prohibited
  until independent review, final scope/evidence validation and the repository task gate
  succeed.
- The first independent review rejected the evidence because the original RED wrote
  SQLite before `GRANT` and the resume-baseline note contradicted that incident. The
  incident remains preserved; acceptance remediation requires a new controller-granted
  canonical RED from the captured pre-implementation source, guaranteed restoration and
  a fresh controller-granted GREEN before independent rereview.
- The controller-granted remediation completed: the captured baseline produced the
  expected 24-failure canonical RED, the current source was restored to its locked hash,
  and the immediate fresh GREEN passed all 24 outcomes. The original incident remains
  auditable and is not reclassified.
- Independent rereview approved the exact closure with P0/P1/P2 all zero while preserving
  the original incident and first REJECTED review as historical evidence.
- Repository task gate passed, but final G2 atomic evidence validation returned rc=1 and
  the controller's active-owner audit found no collision-free peer set. Final PASS remains
  blocked without changing the approved product implementation.

## Ultra Contract Resolution — 2026-07-14

- The accepted CASE_OPENED test's future-event assertion is migrated only by the external
  prerequisite `FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01` after the
  accepted CASE_OPENED task and before this task.
- `backend/tests/test_v8_lifecycle_case_opened.py` remains inherited, read-only regression
  input for this task. This task must not edit that test.
- This task remains responsible only for the task-owned second registry rule and its exact
  task-owned test.

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `384`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-RULE`

- RED expectation: Exact public rule test fails on the named transition/calculation.
- GREEN expectation: Exact rule test passes every named success/boundary/fail-closed case.

## Approved Delta-2 Rule Contract

- `get_lifecycle_rule("FILING_PREPARATION_STARTED")` uses the exact uppercase event key
  and returns this task's rule. No trimming, case folding, normalization, alias or fallback
  lookup is authorized; unknown or malformed lookup input returns `None`.
- The rule accepts only the exact prior CASE_OPENED projection:
  `BusinessStage.NEW_CASE`, `OfficialProcedureStage.NOT_SUBMITTED`,
  `LegalStatus.NOT_ESTABLISHED` and `ConfirmationStatus.CONFIRMED`.
- The resulting projection changes only `business_stage` from
  `BusinessStage.NEW_CASE` to `BusinessStage.FILING_PREPARATION`.
  `official_procedure_stage`, `legal_status` and `lifecycle_verification_status` remain
  exactly unchanged, and `oa_sequence=None`.
- A malformed command/projection, a non-exact event or any prior projection other than the
  exact CASE_OPENED projection returns no decision (`None`).
- The rule is read-only and must not access or interact with the caller-owned transaction:
  no SELECT, write, add, delete, flush, commit or rollback.
- Registry serialization remains `lifecycle_rules.py` order key `2`.

## Exact Closure Slice

`FILING_PREPARATION_STARTED`: business stage only.

## Explicit Non-Closure

No second event/rate/policy, persistence adapter, endpoint, seed or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
- `FPMS-V8-LC-CASE-OPENED-20260712-01`

### External, gate and inherited prerequisites

- `FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01`

- Required order: accepted `FPMS-V8-LC-CASE-OPENED-20260712-01` → external legacy-test
  migration → this task. The inherited CASE_OPENED test remains read-only here.

- Approved source dependency cell (verbatim): [DEFAULT LIFECYCLE SEAM]

### Shared ownership serialization

- `backend/app/modules/cases/lifecycle_rules.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01.md`
- `backend/tests/test_v8_lifecycle_filing_preparation_started.py`
- `backend/app/modules/cases/lifecycle_rules.py`
- `artifacts/FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Modify only lifecycle_rules.py plus the exact test, depend on apply_lifecycle_event(), preserve strict table order and implement exactly one event.

## Verification Commands

- RED and GREEN execute only
  `backend/tests/test_v8_lifecycle_filing_preparation_started.py`; do not edit or directly
  run the inherited CASE_OPENED test as this task's RED/GREEN.
- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_filing_preparation_started.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_filing_preparation_started.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_filing_preparation_started.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_filing_preparation_started.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_filing_preparation_started.py app/modules/cases/lifecycle_rules.py`
- `git diff --check -- backend/tests/test_v8_lifecycle_filing_preparation_started.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01` pass. Only then may this task be reported PASS.
