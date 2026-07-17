# FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `8. Wave 1 — schema spine, globally serialized`
Catalog ordinal: `6`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `355`
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

- RED expectation: The exact schema test fails because the frozen 17-column `DocumentEvidenceVersion` / `t_document_evidence_version`, revision `v8_w1_d1_doc_evidence_version_01`, three named FKs and nullable unique current-key constraint are absent.
- GREEN expectation: ORM metadata and clean migrated SQLite expose exactly the 17 frozen columns, revision/down-revision chain, FK targets/delete actions and `uq_t_document_evidence_version_current_identity_key` behavior; task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.

## Ultra Replan Record — 2026-07-13

- High stopped before evidence initialization, RED, test creation or product edits because the source row named the field families but did not freeze executable column types, nullability, defaults, FK actions or constraint names.
- This replan resolves only that physical-schema ambiguity. It does not change the single carrier closure, non-closure boundary, allowlist, dependency order, verification runbook or customer-gate classification.
- Story Shape Classification remains unchanged and `chosen_runbook` remains `P0-prereq-heavy-story`.
- The minimum schema uses the repository's application-generated UUID string convention, SQLite-safe timestamps, explicit creator/reviewer separation and only the uniqueness required by the canonical plan.

## Frozen Migration Identity

| Item | Frozen value |
| --- | --- |
| Alembic `revision` | `v8_w1_d1_doc_evidence_version_01` |
| Alembic `down_revision` | `v8_w1_l3_activity_evidence_01` |
| Migration filename | `backend/alembic/versions/v8_w1_d1_document_evidence_version.py` |

The implementing agent must first confirm that the frozen `down_revision` is the single repository head. A mismatch is a planning blocker; the migration chain must not be guessed or branched.

## Frozen Physical Schema Contract

ORM class: `DocumentEvidenceVersion`. Table: `t_document_evidence_version`.

| Column | SQLAlchemy / Alembic type | ORM annotation | Nullable | Server default | FK / meaning |
| --- | --- | --- | --- | --- | --- |
| `id` | `String(36)` | `Mapped[str]` | no | none; application UUID | primary key through `UUIDPrimaryKeyMixin` |
| `case_id` | `String(36)` | `Mapped[str]` | no | none | `t_case.id`, named FK below, `ON DELETE CASCADE` |
| `document_id` | `String(36)` | `Mapped[str]` | no | none | `t_document.id`, named FK below, `ON DELETE CASCADE` |
| `attachment_id` | `String(36)` | `Mapped[str]` | no | none | `t_doc_attachment.id`, named FK below, default `NO ACTION` |
| `lineage_key` | `String(128)` | `Mapped[str]` | no | none | stable logical-document lineage supplied by the later service |
| `role` | `String(64)` | `Mapped[str]` | no | none | evidence role code; vocabulary belongs to `FPMS-V8-DE-CONTRACTS-20260712-01` |
| `version_number` | `Integer` | `Mapped[int]` | no | none | positive/monotonic validation belongs to the later service |
| `state` | `String(32)` | `Mapped[str]` | no | none | version state code; vocabulary belongs to the later contracts task |
| `creator_id` | `String(36)` | `Mapped[str]` | no | none | creating actor identity; deliberately distinct from reviewer |
| `review_state` | `String(32)` | `Mapped[str]` | no | none | review state code supplied by the later service |
| `reviewer_id` | `String(36)` | `Mapped[str \| None]` | yes | none | reviewing actor identity; no creator fallback |
| `reviewed_at` | `DateTime(timezone=False)` | `Mapped[datetime \| None]` | yes | none | review decision time |
| `final_submitted_at` | `DateTime(timezone=False)` | `Mapped[datetime \| None]` | yes | none | final external-submission time |
| `content_hash` | `String(128)` | `Mapped[str]` | no | none | immutable attachment-content digest supplied by the later service |
| `current_identity_key` | `String(256)` | `Mapped[str \| None]` | yes | none | exactly `case_id|lineage_key` only while this row is current |
| `created_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | explicit audit timestamp |
| `updated_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | explicit audit timestamp |

`DocumentEvidenceVersion` uses `UUIDPrimaryKeyMixin` and `Base`, not `AuditMixin`; `AuditMixin` would introduce unapproved `created_by`/`updated_by` columns and Python-side timestamp behavior that conflicts with the frozen carrier.

### Frozen constraints and indexes

| Kind | Columns / target | Exact name | Action |
| --- | --- | --- | --- |
| primary key | `id` | repository-default unnamed PK | application-generated UUID string |
| foreign key | `case_id -> t_case.id` | `fk_t_document_evidence_version_case_id` | `ON DELETE CASCADE` |
| foreign key | `document_id -> t_document.id` | `fk_t_document_evidence_version_document_id` | `ON DELETE CASCADE` |
| foreign key | `attachment_id -> t_doc_attachment.id` | `fk_t_document_evidence_version_attachment_id` | default `NO ACTION` |
| unique | `current_identity_key` | `uq_t_document_evidence_version_current_identity_key` | multiple `NULL` historical rows remain valid under SQLite |

No secondary index, composite same-case FK, lineage/version unique constraint, CHECK constraint or user FK is authorized in D1. Wrong-case case/document/attachment combinations, version monotonicity, role/state vocabulary, creator/reviewer separation and current-key transitions remain service-layer invariants owned by their named follow-up tasks.

### Exact RED / GREEN schema assertions

The D1 schema test must prove:

1. RED fails because `DocumentEvidenceVersion` / `t_document_evidence_version` is absent.
2. ORM metadata and migrated SQLite contain exactly the 17 frozen columns above with matching types, nullability and timestamp defaults.
3. The three named FKs target the frozen tables and use the frozen delete actions.
4. `uq_t_document_evidence_version_current_identity_key` rejects two equal non-null current keys while accepting multiple `NULL` historical keys.
5. No extra D1 table, secondary index, business CHECK or service behavior is introduced.

## Exact Closure Slice

Add only the frozen 17-column `DocumentEvidenceVersion` / `t_document_evidence_version` carrier, its three named case/document/attachment FKs, explicit creator/reviewer fields, SQLite-safe audit timestamps and the named nullable unique `current_identity_key` constraint.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
- `FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): L2

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `4`; project this order only across owners present in the active manifest.
- `backend/app/modules/documents/models.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w1_d1_document_evidence_version.py`
- `backend/app/modules/documents/models.py`
- `backend/tests/test_v8_w1_d1_document_evidence_version.py`
- `artifacts/FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Run in the frozen global Alembic order; use SQLite-safe forward-only migration semantics, unique-head check and clean temporary upgrade head.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_w1_d1_document_evidence_version.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_d1_document_evidence_version.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_d1_document_evidence_version.py app/modules/documents/models.py tests/test_v8_w1_d1_document_evidence_version.py && .venv/bin/ruff format alembic/versions/v8_w1_d1_document_evidence_version.py app/modules/documents/models.py tests/test_v8_w1_d1_document_evidence_version.py && .venv/bin/ruff check alembic/versions/v8_w1_d1_document_evidence_version.py app/modules/documents/models.py tests/test_v8_w1_d1_document_evidence_version.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w1_d1_document_evidence_version.py backend/app/modules/documents/models.py backend/tests/test_v8_w1_d1_document_evidence_version.py tasks/postdemo/v8/FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
