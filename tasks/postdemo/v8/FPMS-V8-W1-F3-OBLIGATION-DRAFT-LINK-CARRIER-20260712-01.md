# FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `8. Wave 1 — schema spine, globally serialized`
Catalog ordinal: `11`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `360`
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

Add only obligation-line to draft-item linkage.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): F2

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `9`; project this order only across owners present in the active manifest.
- `backend/app/modules/fees/models.py` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w1_f3_obligation_draft_link.py`
- `backend/app/modules/fees/models.py`
- `backend/tests/test_v8_w1_f3_obligation_draft_link.py`
- `artifacts/FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Run in the frozen global Alembic order; use SQLite-safe forward-only migration semantics, unique-head check and clean temporary upgrade head.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f3_obligation_draft_link.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f3_obligation_draft_link.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_f3_obligation_draft_link.py app/modules/fees/models.py tests/test_v8_w1_f3_obligation_draft_link.py && .venv/bin/ruff format alembic/versions/v8_w1_f3_obligation_draft_link.py app/modules/fees/models.py tests/test_v8_w1_f3_obligation_draft_link.py && .venv/bin/ruff check alembic/versions/v8_w1_f3_obligation_draft_link.py app/modules/fees/models.py tests/test_v8_w1_f3_obligation_draft_link.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w1_f3_obligation_draft_link.py backend/app/modules/fees/models.py backend/tests/test_v8_w1_f3_obligation_draft_link.py tasks/postdemo/v8/FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
