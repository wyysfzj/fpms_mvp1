# FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `8. Wave 1 — schema spine, globally serialized`
Catalog ordinal: `7`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `356`
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

- RED expectation: The exact D2 schema test fails because `DocumentEvidenceDerivation` / `t_document_evidence_derivation` and its frozen 10-column carrier are absent at revision `v8_w1_d1_doc_evidence_version_01`.
- GREEN expectation: Revision `v8_w1_d2_evidence_derivation_01` creates exactly the frozen 10 columns and three named simple FKs, with no UNIQUE/index/CHECK/trigger; task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.
- Same-case boundary: the schema proves referenced-row existence only; `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01` must reject a parent or child whose `case_id` differs from the command case with HTTP 400 before `flush`.

## Ultra Replan Record — 2026-07-13

- High stopped before evidence initialization, RED, test creation or product edits because the source row did not freeze executable column names, types, nullability, defaults, delete actions or constraint names.
- This replan resolves only that physical-schema ambiguity. It does not change the one-table carrier closure, non-closure boundary, allowlist, dependency order, verification runbook or customer-gate classification.
- Story Shape Classification remains unchanged and `chosen_runbook` remains `P0-prereq-heavy-story`.
- The minimum carrier records one directed parent-to-child derivation, its actor/time and an immutable Text source snapshot. It does not add speculative edge uniqueness, cycle policy or derivation vocabulary.

## Frozen Migration Identity

| Item | Frozen value |
| --- | --- |
| Alembic `revision` | `v8_w1_d2_evidence_derivation_01` |
| Alembic `down_revision` | `v8_w1_d1_doc_evidence_version_01` |
| Migration filename | `backend/alembic/versions/v8_w1_d2_document_evidence_derivation.py` |

The implementing agent must first confirm that the frozen `down_revision` is the single repository head. A mismatch is a planning blocker; the migration chain must not be guessed or branched.

## Frozen Physical Schema Contract

ORM class: `DocumentEvidenceDerivation`. Table: `t_document_evidence_derivation`.

| Column | SQLAlchemy / Alembic type | ORM annotation | Nullable | Server default | FK / meaning |
| --- | --- | --- | --- | --- | --- |
| `id` | `String(36)` | `Mapped[str]` | no | none; application UUID | primary key through `UUIDPrimaryKeyMixin` |
| `case_id` | `String(36)` | `Mapped[str]` | no | none | `t_case.id`, named FK below, `ON DELETE CASCADE` |
| `parent_evidence_version_id` | `String(36)` | `Mapped[str]` | no | none | source `t_document_evidence_version.id`, named FK below, default `NO ACTION` |
| `child_evidence_version_id` | `String(36)` | `Mapped[str]` | no | none | derived `t_document_evidence_version.id`, named FK below, default `NO ACTION` |
| `derivation_type` | `String(64)` | `Mapped[str]` | no | none | derivation code; vocabulary belongs to `FPMS-V8-DE-CONTRACTS-20260712-01` |
| `actor_id` | `String(36)` | `Mapped[str]` | no | none | actor identity supplied by the later service; no user FK |
| `derived_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | none | business time at which the child was derived |
| `source_snapshot` | `Text` | `Mapped[str]` | no | none | immutable source/derivation snapshot; content contract belongs to the later contracts task |
| `created_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | explicit audit timestamp |
| `updated_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | explicit audit timestamp |

`DocumentEvidenceDerivation` uses `UUIDPrimaryKeyMixin` and `Base`, not `AuditMixin`; `AuditMixin` would introduce unapproved `created_by`/`updated_by` columns and Python-side timezone-aware timestamps that conflict with this carrier.

### Frozen constraints and indexes

| Kind | Columns / target | Exact name | Action |
| --- | --- | --- | --- |
| primary key | `id` | repository-default unnamed PK | application-generated UUID string |
| foreign key | `case_id -> t_case.id` | `fk_t_document_evidence_derivation_case_id` | `ON DELETE CASCADE` |
| foreign key | `parent_evidence_version_id -> t_document_evidence_version.id` | `fk_t_document_evidence_derivation_parent_evidence_version_id` | default `NO ACTION` |
| foreign key | `child_evidence_version_id -> t_document_evidence_version.id` | `fk_t_document_evidence_derivation_child_evidence_version_id` | default `NO ACTION` |

No UNIQUE constraint, secondary index, CHECK constraint or user FK is authorized in D2. Duplicate-edge idempotency, self/cycle rejection, derivation vocabulary and snapshot validation belong to their later contracts/service tasks.

### Deliberate same-case enforcement boundary

The canonical design requires parent and child evidence versions to belong to the same case. D2 persists non-null `case_id` plus parent and child version references, but the frozen D1 carrier does not expose a composite unique parent key on `(case_id, id)`. SQLite therefore cannot support sound D2 composite foreign keys to that pair without changing D1's already-frozen closure.

D2 deliberately does not expand D1 or invent triggers. Its three named simple foreign keys enforce row existence; `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01` must load both referenced versions, require `parent.case_id == child.case_id == case_id`, and return 400 for any cross-case relation before `flush`. This is an explicit service invariant, not an assertion that the D2 schema alone prevents cross-case rows.

### Exact RED / GREEN schema assertions

The D2 schema test must prove:

1. RED fails because `DocumentEvidenceDerivation` / `t_document_evidence_derivation` is absent.
2. ORM metadata and migrated SQLite contain exactly the 10 frozen columns above with matching types, nullability and timestamp defaults.
3. The three named FKs target the frozen tables and use the frozen delete actions.
4. Parent/child references to missing evidence-version rows fail with SQLite foreign keys enabled.
5. No extra D2 table, UNIQUE, secondary index, business CHECK, trigger or service behavior is introduced.

## Exact Closure Slice

Add only the frozen 10-column `DocumentEvidenceDerivation` / `t_document_evidence_derivation` carrier, its named case/parent/child FKs, actor/time, immutable Text source snapshot and SQLite-safe audit timestamps.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): D1

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `5`; project this order only across owners present in the active manifest.
- `backend/app/modules/documents/models.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w1_d2_document_evidence_derivation.py`
- `backend/app/modules/documents/models.py`
- `backend/tests/test_v8_w1_d2_document_evidence_derivation.py`
- `artifacts/FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Run in the frozen global Alembic order; use SQLite-safe forward-only migration semantics, unique-head check and clean temporary upgrade head.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_w1_d2_document_evidence_derivation.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_d2_document_evidence_derivation.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_d2_document_evidence_derivation.py app/modules/documents/models.py tests/test_v8_w1_d2_document_evidence_derivation.py && .venv/bin/ruff format alembic/versions/v8_w1_d2_document_evidence_derivation.py app/modules/documents/models.py tests/test_v8_w1_d2_document_evidence_derivation.py && .venv/bin/ruff check alembic/versions/v8_w1_d2_document_evidence_derivation.py app/modules/documents/models.py tests/test_v8_w1_d2_document_evidence_derivation.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w1_d2_document_evidence_derivation.py backend/app/modules/documents/models.py backend/tests/test_v8_w1_d2_document_evidence_derivation.py tasks/postdemo/v8/FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
