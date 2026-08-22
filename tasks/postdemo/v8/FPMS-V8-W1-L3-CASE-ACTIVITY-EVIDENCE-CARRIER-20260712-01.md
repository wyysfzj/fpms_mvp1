# FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `8. Wave 1 — schema spine, globally serialized`
Catalog ordinal: `5`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `354`
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

- RED expectation: Exact schema test fails because `CaseActivityEventEvidence`, revision `v8_w1_l3_activity_evidence_01`, the 10 frozen columns or the named constraints are absent.
- GREEN expectation: Exact ORM and migrated-SQLite tests prove the frozen columns, physical types, nullability/defaults, exact five-part UNIQUE and same-case activity composite FK; a same-case link succeeds, a missing/cross-case activity fails and the exact duplicate identity fails; task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.

## Exact Closure Slice

Add only the frozen `CaseActivityEventEvidence` / `t_case_activity_event_evidence` carrier with its 10 columns, composite same-case activity FK `(case_id, activity_id) → t_case_activity_event(case_id, id)` and exact UNIQUE `(case_id, activity_id, evidence_kind, object_type, object_id)`; SQLite test accepts a same-case link and rejects missing/cross-case activities and an exact duplicate evidence-link identity.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Freeze — 2026-07-13

High stopped before evidence initialization, RED, and any L3 source/test/migration edit because the canonical design froze the evidence-link categories but not their complete physical types, nullability or defaults. The closure slice did not change. Story Shape Classification remains unchanged and `chosen_runbook` remains `P0-prereq-heavy-story`.

ORM/table identity:

- ORM class: `CaseActivityEventEvidence`.
- Table: `t_case_activity_event_evidence`.
- ORM base: `UUIDPrimaryKeyMixin, Base`; do not use `AuditMixin` because its application/timezone defaults and principal columns conflict with the frozen V8 carrier.
- Alembic revision: `v8_w1_l3_activity_evidence_01`.
- Alembic down revision: `v8_w1_l2_case_activity_event_01`; recheck the unique head immediately before implementation.

Frozen columns:

| Column | SQLAlchemy / Alembic type | ORM annotation | Nullable | Default / FK |
|---|---|---|---:|---|
| `id` | `String(36)` | `Mapped[str]` | no | application `uuid4`; no migration/server default |
| `case_id` | `String(36)` | `Mapped[str]` | no | no standalone FK/default; governed by the composite FK below |
| `activity_id` | `String(36)` | `Mapped[str]` | no | no standalone FK/default; governed by the composite FK below |
| `evidence_kind` | `String(32)` | `Mapped[str]` | no | none |
| `object_type` | `String(64)` | `Mapped[str]` | no | none |
| `object_id` | `String(36)` | `Mapped[str]` | no | polymorphic application object identifier; no standalone FK/default |
| `content_hash` | `String(128)` | `Mapped[str]` | no | none |
| `captured_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | none; caller supplies the evidence-capture time |
| `created_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `server_default=text("CURRENT_TIMESTAMP")` |
| `updated_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `server_default=text("CURRENT_TIMESTAMP")`; no `onupdate` |

Frozen constraints:

| Name | Contract |
|---|---|
| `fk_t_case_activity_event_evidence_activity_same_case` | composite FK `(case_id, activity_id) → t_case_activity_event(case_id, id)` with no delete action or deferrable behavior |
| `uq_t_case_activity_event_evidence_link` | UNIQUE `(case_id, activity_id, evidence_kind, object_type, object_id)` in exactly this order |

Frozen invariants and exclusions:

- The composite activity FK is the only L3 FK: it proves the activity belongs to `case_id` through L2's unique parent `(case_id, id)`. Do not add redundant standalone case/activity FKs.
- `object_type` plus `object_id` is a polymorphic application-object reference. L3 does not add an object FK, object registry, second identifier or external-reference field.
- `content_hash` and `captured_at` are mandatory evidence facts. Do not default capture time or silently accept a hashless link.
- `created_at` and `updated_at` are the only L3 audit columns. Do not add `created_by`, `updated_by`, `captured_by` or reuse `AuditMixin`; activity principals remain on the parent L2 event.
- Do not add enum/CHECK constraints, business indexes, payload/snapshot text, relationship cascades, application behavior or service validation. Those are not part of this carrier closure.
- The exact test must enable SQLite foreign keys and assert reflected constrained/referred composite-column order, not only ORM metadata.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): L2

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `3`; project this order only across owners present in the active manifest.
- `backend/app/modules/cases/models.py` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w1_l3_case_activity_evidence.py`
- `backend/app/modules/cases/models.py`
- `backend/tests/test_v8_w1_l3_case_activity_evidence.py`
- `artifacts/FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Run in the frozen global Alembic order; use SQLite-safe forward-only migration semantics, unique-head check and clean temporary upgrade head.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_w1_l3_case_activity_evidence.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_l3_case_activity_evidence.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_l3_case_activity_evidence.py app/modules/cases/models.py tests/test_v8_w1_l3_case_activity_evidence.py && .venv/bin/ruff format alembic/versions/v8_w1_l3_case_activity_evidence.py app/modules/cases/models.py tests/test_v8_w1_l3_case_activity_evidence.py && .venv/bin/ruff check alembic/versions/v8_w1_l3_case_activity_evidence.py app/modules/cases/models.py tests/test_v8_w1_l3_case_activity_evidence.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w1_l3_case_activity_evidence.py backend/app/modules/cases/models.py backend/tests/test_v8_w1_l3_case_activity_evidence.py tasks/postdemo/v8/FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
