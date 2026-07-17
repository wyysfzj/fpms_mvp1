# FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `8. Wave 1 — schema spine, globally serialized`
Catalog ordinal: `4`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `353`
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

- RED expectation: Exact schema test fails because `CaseActivityEvent`, revision `v8_w1_l2_case_activity_event_01`, the 23 frozen columns or the named constraints are absent.
- GREEN expectation: Exact ORM and migrated-SQLite tests prove the frozen columns, physical types, nullability/defaults, three UNIQUE constraints, case FK and nullable same-case source composite FK; NULL/same-case sources succeed, missing/cross-case sources fail; task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.

## Exact Closure Slice

Add only the frozen `CaseActivityEvent` / `t_case_activity_event` carrier with its 23 columns, sequence/idempotency uniqueness, composite parent key `(case_id,id)` and nullable same-case composite self-FK `(case_id,source_activity_id) → (case_id,id)`; SQLite test accepts NULL/same-case and rejects missing/cross-case sources.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Freeze — 2026-07-13

High stopped before evidence initialization, RED, and any L2 source/test/migration edit because the canonical design named field categories but did not freeze a complete physical table. The closure slice did not change. Story Shape Classification remains unchanged and `chosen_runbook` remains `P0-prereq-heavy-story`.

ORM/table identity:

- ORM class: `CaseActivityEvent`.
- Table: `t_case_activity_event`.
- ORM base: `UUIDPrimaryKeyMixin, Base`; do not use `AuditMixin` because its application/timezone defaults conflict with the V8 `CURRENT_TIMESTAMP` contract.
- Alembic revision: `v8_w1_l2_case_activity_event_01`.
- Alembic down revision: `v8_w1_l1_case_lifecycle_01`; recheck the unique head immediately before implementation.

Frozen columns:

| Column | SQLAlchemy / Alembic type | ORM annotation | Nullable | Default / FK |
|---|---|---|---:|---|
| `id` | `String(36)` | `Mapped[str]` | no | application `uuid4`; no migration/server default |
| `case_id` | `String(36)` | `Mapped[str]` | no | FK `t_case.id`, `ondelete="CASCADE"`; no default |
| `sequence` | `Integer` | `Mapped[int]` | no | none |
| `lane` | `String(16)` | `Mapped[str]` | no | none |
| `activity_type` | `String(64)` | `Mapped[str]` | no | none |
| `source_activity_id` | `String(36)` | `Mapped[str | None]` | yes | no standalone FK/default; governed by the composite FK below |
| `occurred_at` | `DateTime(timezone=False)` | `Mapped[datetime | None]` | yes | none |
| `effective_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | none |
| `recorded_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `server_default=text("CURRENT_TIMESTAMP")` |
| `confirmation_status` | `String(32)` | `Mapped[str]` | no | none |
| `old_business_stage` | `String(32)` | `Mapped[str | None]` | yes | none |
| `new_business_stage` | `String(32)` | `Mapped[str | None]` | yes | none |
| `old_official_procedure_stage` | `String(64)` | `Mapped[str | None]` | yes | none |
| `new_official_procedure_stage` | `String(64)` | `Mapped[str | None]` | yes | none |
| `old_legal_status` | `String(32)` | `Mapped[str | None]` | yes | none |
| `new_legal_status` | `String(32)` | `Mapped[str | None]` | yes | none |
| `actor_id` | `String(36)` | `Mapped[str]` | no | no user FK/default |
| `reviewer_id` | `String(36)` | `Mapped[str | None]` | yes | no user FK/default |
| `idempotency_key` | `String(128)` | `Mapped[str]` | no | none |
| `supersedes_event_id` | `String(36)` | `Mapped[str | None]` | yes | no FK/default in L2 |
| `payload_json` | `Text` | `Mapped[str]` | no | no default; service must persist canonical JSON text |
| `created_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `server_default=text("CURRENT_TIMESTAMP")` |
| `updated_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `server_default=text("CURRENT_TIMESTAMP")`; no `onupdate` |

Frozen constraints:

| Name | Contract |
|---|---|
| `fk_t_case_activity_event_case_id` | simple `case_id → t_case.id`, `ondelete="CASCADE"` |
| `uq_t_case_activity_event_case_sequence` | UNIQUE `(case_id, sequence)` |
| `uq_t_case_activity_event_case_idempotency_key` | UNIQUE `(case_id, idempotency_key)` |
| `uq_t_case_activity_event_case_id` | UNIQUE `(case_id, id)`, required as the SQLite composite parent key |
| `fk_t_case_activity_event_source_same_case` | nullable composite FK `(case_id, source_activity_id) → t_case_activity_event(case_id, id)` with no delete action or deferrable behavior |

Frozen invariants and exclusions:

- `source_activity_id` is the causal/source-activity link exposed by the overlay. `supersedes_event_id` is the separate correction target named by the canonical design; do not merge them.
- Only `source_activity_id` receives the L2 composite self-FK. Do not add an unapproved FK for `supersedes_event_id`; its service validation belongs to downstream lifecycle work.
- `occurred_at` is nullable because the approved command requires `effective_at`, not an independently proven occurrence time. Do not copy or invent another timestamp to satisfy it.
- Do not add `created_by`/`updated_by`; `actor_id` and conditional `reviewer_id` are the frozen event principals.
- Do not add enum/CHECK constraints, business indexes, extra defaults, a `center_changes` column or a second payload column. Later lifecycle-contract/service tasks own value validation and behavior.
- The exact test must enable SQLite foreign keys and assert reflected constrained/referred composite-column order, not only ORM metadata.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): L1

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `2`; project this order only across owners present in the active manifest.
- `backend/app/modules/cases/models.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w1_l2_case_activity_event.py`
- `backend/app/modules/cases/models.py`
- `backend/tests/test_v8_w1_l2_case_activity_event.py`
- `artifacts/FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Run in the frozen global Alembic order; use SQLite-safe forward-only migration semantics, unique-head check and clean temporary upgrade head.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_w1_l2_case_activity_event.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_l2_case_activity_event.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_l2_case_activity_event.py app/modules/cases/models.py tests/test_v8_w1_l2_case_activity_event.py && .venv/bin/ruff format alembic/versions/v8_w1_l2_case_activity_event.py app/modules/cases/models.py tests/test_v8_w1_l2_case_activity_event.py && .venv/bin/ruff check alembic/versions/v8_w1_l2_case_activity_event.py app/modules/cases/models.py tests/test_v8_w1_l2_case_activity_event.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w1_l2_case_activity_event.py backend/app/modules/cases/models.py backend/tests/test_v8_w1_l2_case_activity_event.py tasks/postdemo/v8/FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
