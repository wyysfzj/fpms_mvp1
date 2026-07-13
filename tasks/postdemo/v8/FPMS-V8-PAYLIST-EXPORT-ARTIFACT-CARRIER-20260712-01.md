# FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `13. Wave 5 — PayList internal/official/payment boundary`
Catalog ordinal: `159`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `622`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SCHEMA`

- RED expectation: Exact schema test fails because the named table/column/index is absent.
- GREEN expectation: Exact schema test, task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.

## Exact Closure Slice

Add only `t_pay_list_export_artifact` with kind/status/hash/template version/path, generated identity and nullable official-site acceptance evidence/time; no payment or ticket state.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): global Alembic lock after rate book

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `14`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w5_pay_list_export_artifact.py`
- `backend/app/modules/annuity/models.py`
- `backend/tests/test_v8_pay_list_export_artifact_schema.py`
- `artifacts/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_pay_list_export_artifact_schema.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_pay_list_export_artifact_schema.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w5_pay_list_export_artifact.py app/modules/annuity/models.py tests/test_v8_pay_list_export_artifact_schema.py && .venv/bin/ruff format alembic/versions/v8_w5_pay_list_export_artifact.py app/modules/annuity/models.py tests/test_v8_pay_list_export_artifact_schema.py && .venv/bin/ruff check alembic/versions/v8_w5_pay_list_export_artifact.py app/modules/annuity/models.py tests/test_v8_pay_list_export_artifact_schema.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w5_pay_list_export_artifact.py backend/app/modules/annuity/models.py backend/tests/test_v8_pay_list_export_artifact_schema.py tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
