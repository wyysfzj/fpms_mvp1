# FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `8. Wave 1 — schema spine, globally serialized`
Catalog ordinal: `3`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `352`
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

- RED expectation: Exact schema test fails because the five named `t_case` columns are absent from both the ORM table and the migrated SQLite schema.
- GREEN expectation: Exact schema test proves the five frozen names, physical types, nullability and absence of defaults/indexes/checks; task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.

## Exact Closure Slice

Add only these five nullable lifecycle projection/revision/verification columns to `t_case`: `String(32)` code carriers named `business_stage`, `legal_status` and `lifecycle_verification_status`, one `String(64)` code carrier named `official_procedure_stage`, plus one `Integer` revision carrier named `lifecycle_revision`.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Freeze — 2026-07-13

Execution stopped before RED and before any source, test or migration edit because the approved design and plan froze the five names and nullability but did not state their physical types. The closure slice did not change. Story Shape Classification remains unchanged and `chosen_runbook` remains `P0-prereq-heavy-story`.

The following physical contract is now frozen for this task:

| `t_case` column | SQLAlchemy / Alembic type | ORM annotation | Nullable | Server/client default | New index / unique / CHECK / FK |
|---|---|---|---:|---|---|
| `business_stage` | `String(32)` / `sa.String(length=32)` | `Mapped[str | None]` | yes | none | none |
| `official_procedure_stage` | `String(64)` / `sa.String(length=64)` | `Mapped[str | None]` | yes | none | none |
| `legal_status` | `String(32)` / `sa.String(length=32)` | `Mapped[str | None]` | yes | none | none |
| `lifecycle_revision` | `Integer` / `sa.Integer()` | `Mapped[int | None]` | yes | none | none |
| `lifecycle_verification_status` | `String(32)` / `sa.String(length=32)` | `Mapped[str | None]` | yes | none | none |

Frozen invariants:

- All five columns remain nullable so existing cases can stay uninitialized until separately authorized projection/backfill work runs.
- No Python default, SQL server default or data backfill is authorized; in particular, do not silently initialize `lifecycle_revision` to `0`.
- The local `Case` model uses `String(32)` for status codes. That width covers the frozen business-stage, legal-status and known verification-status codes; `official_procedure_stage` uses `String(64)` because its frozen vocabulary includes the 39-character `SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE` value.
- Do not add database enums, value-level `CHECK` constraints or application validation. The later lifecycle-contract task owns state vocabulary and transition validation.
- Do not add an index, uniqueness constraint or foreign key. This task owns carriers only.
- `lifecycle_revision` is an application-maintained integer revision in later work; this task does not increment or interpret it.
- Persist the database column as `lifecycle_verification_status`; the shorter overlay response name `center_snapshot.verification_status` is not a database alias.
- Legacy `t_case.status` remains untouched and is not one of the five columns.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01`
- `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`

### External, gate and inherited prerequisites

- `external` — `PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01`: Materialization task PASS.

- Approved source dependency cell (verbatim): Wave 0

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `1`; project this order only across owners present in the active manifest.
- `backend/app/modules/cases/models.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w1_l1_case_lifecycle_projection.py`
- `backend/app/modules/cases/models.py`
- `backend/tests/test_v8_w1_l1_case_lifecycle_projection.py`
- `artifacts/FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Run in the frozen global Alembic order; use SQLite-safe forward-only migration semantics, unique-head check and clean temporary upgrade head.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_w1_l1_case_lifecycle_projection.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_l1_case_lifecycle_projection.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_l1_case_lifecycle_projection.py app/modules/cases/models.py tests/test_v8_w1_l1_case_lifecycle_projection.py && .venv/bin/ruff format alembic/versions/v8_w1_l1_case_lifecycle_projection.py app/modules/cases/models.py tests/test_v8_w1_l1_case_lifecycle_projection.py && .venv/bin/ruff check alembic/versions/v8_w1_l1_case_lifecycle_projection.py app/modules/cases/models.py tests/test_v8_w1_l1_case_lifecycle_projection.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w1_l1_case_lifecycle_projection.py backend/app/modules/cases/models.py backend/tests/test_v8_w1_l1_case_lifecycle_projection.py tasks/postdemo/v8/FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
