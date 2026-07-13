# FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `146`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `597`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: Exact adapter test proves the old direct write/missing activity/premature state.
- GREEN expectation: Exact adapter test plus listed inherited regressions pass; only the named entrypoint changes.

## Exact Closure Slice

`IC_LAYOUT_REGISTRATION_FILED`: reviewed final layout-registration submission evidence forms/reuses only `IC_LAYOUT_REGISTRATION_FEE` with `fee_year_key=0`.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
- `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01`
- `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
- `FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01`
- `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM`, `FPMS-V8-DE-REVIEW-SERVICE`, `FPMS-V8-FO-RECOGNIZE-OBLIGATION`, `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION`, `FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE`

### Shared ownership serialization

- `backend/app/modules/documents/evidence_workflow_service.py` order key `3`; project this order only across owners present in the active manifest.
- `backend/app/modules/documents/fee_linking_service.py` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01.md`
- `backend/app/modules/documents/evidence_workflow_service.py`
- `backend/app/modules/documents/fee_linking_service.py`
- `backend/tests/test_v8_ic_layout_registration_filed_obligation.py`
- `artifacts/FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Accept only same-case current independently reviewed final evidence; conflict is 409/no write; recognize_obligation owns the sole fee activity.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_ic_layout_registration_filed_obligation.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_ic_layout_registration_filed_obligation.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_registration_filed_obligation.py && .venv/bin/ruff format app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_registration_filed_obligation.py && .venv/bin/ruff check app/modules/documents/evidence_workflow_service.py app/modules/documents/fee_linking_service.py tests/test_v8_ic_layout_registration_filed_obligation.py`
- `git diff --check -- backend/app/modules/documents/evidence_workflow_service.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_ic_layout_registration_filed_obligation.py tasks/postdemo/v8/FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01` pass. Only then may this task be reported PASS.
