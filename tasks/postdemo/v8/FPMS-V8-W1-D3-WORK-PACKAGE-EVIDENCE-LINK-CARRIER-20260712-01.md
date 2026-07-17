# FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `8. Wave 1 — schema spine, globally serialized`
Catalog ordinal: `8`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `357`
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

- RED expectation: The exact D3 schema test fails because `OfficialWorkPackageManifest.evidence_version_id`, its named FK and its named non-unique index are absent; the test also freezes the existing `attachment_id` compatibility shape.
- GREEN expectation: ORM metadata and migrated SQLite expose exactly the frozen nullable `String(36)` column, named default-`NO ACTION` FK and named non-unique index while legacy `attachment_id` remains unchanged; missing non-null evidence references fail, legacy `NULL` links remain valid, task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.

## Ultra Replan Record — 2026-07-13

- High stopped before evidence initialization, RED, test creation or product edits because the source row froze the compatibility-link name but not its executable type, nullability, FK name/delete action, index or default behavior.
- This replan resolves only that one-column physical-schema ambiguity. It does not change the single compatibility-link closure, non-closure boundary, allowlist, dependency order, verification runbook or customer-gate classification.
- Story Shape Classification remains unchanged and `chosen_runbook` remains `P0-prereq-heavy-story`.
- The minimum change mirrors the existing manifest attachment-link convention while making the new evidence-version reference explicit and auditable. It does not replace or reinterpret the legacy attachment link.

## Frozen Migration Identity

| Item | Frozen value |
| --- | --- |
| Alembic `revision` | `v8_w1_d3_workpkg_evidence_01` |
| Alembic `down_revision` | `v8_w1_d2_evidence_derivation_01` |
| Migration filename | `backend/alembic/versions/v8_w1_d3_work_package_evidence_link.py` |

The implementing agent must first confirm that the frozen `down_revision` is the single repository head. A mismatch is a planning blocker; the migration chain must not be guessed or branched.

## Frozen Physical Compatibility-Link Contract

ORM owner: `OfficialWorkPackageManifest`. Existing table: `t_official_work_package_manifest`.

| ORM attribute / column | SQLAlchemy / Alembic type | ORM annotation | Nullable | Default | FK / delete action | Index |
| --- | --- | --- | --- | --- | --- | --- |
| `evidence_version_id` | `String(36)` | `Mapped[str \| None]` | yes | no Python or server default | named FK `fk_t_official_work_package_manifest_evidence_version_id` to `t_document_evidence_version.id`; default `NO ACTION` (no `ondelete`) | named non-unique index `ix_t_official_work_package_manifest_evidence_version_id` |

The ORM mapping is exactly:

```python
evidence_version_id: Mapped[str | None] = mapped_column(
    String(36),
    ForeignKey(
        "t_document_evidence_version.id",
        name="fk_t_official_work_package_manifest_evidence_version_id",
    ),
    nullable=True,
    index=True,
)
```

The migration must use SQLite-safe Alembic operations that leave the named FK present after a clean SQLite `upgrade head`; it must create the named non-unique index explicitly. No relationship property is part of D3.

### Frozen legacy compatibility invariant

`attachment_id` remains unchanged in both ORM and migrated schema:

- `Mapped[str | None]` / `String(36)`;
- nullable with no Python or server default;
- FK to `t_doc_attachment.id` with default `NO ACTION`;
- existing non-unique index `ix_t_official_work_package_manifest_attachment_id` retained;
- no backfill, coalescing rule, precedence rule or deletion is introduced.

### Frozen constraints and non-constraints

- D3 adds exactly one nullable column, one named FK and one named non-unique index.
- D3 adds no UNIQUE or CHECK constraint and no cascade/set-null action.
- D3 does not require `evidence_version_id` and `attachment_id` to agree, and does not require either field to be present; compatibility-selection rules belong to later service tasks.
- The referenced D1 evidence-version row must exist when a non-null link is written; SQLite FK enforcement proves only existence, not package/case/document semantic agreement.

### Exact RED / GREEN schema assertions

The D3 schema test must prove:

1. RED fails because `OfficialWorkPackageManifest.evidence_version_id` and the migrated column are absent.
2. ORM metadata and migrated SQLite expose `evidence_version_id` as nullable `String(36)` with no default.
3. The exact named FK targets `t_document_evidence_version.id` and has default `NO ACTION`.
4. The exact named non-unique index `ix_t_official_work_package_manifest_evidence_version_id` exists.
5. A non-null missing evidence-version reference fails with SQLite foreign keys enabled, while a legacy manifest row with `evidence_version_id=NULL` remains valid.
6. Existing `attachment_id`, its FK and `ix_t_official_work_package_manifest_attachment_id` remain unchanged.
7. No extra column, relationship, UNIQUE, CHECK, service behavior or backfill is introduced.

## Exact Closure Slice

Add only the frozen nullable `String(36)` manifest `evidence_version_id`, its named default-`NO ACTION` FK to `t_document_evidence_version.id` and its named non-unique index, while retaining `attachment_id` unchanged.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01`
- `FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): D1

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `6`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w1_d3_work_package_evidence_link.py`
- `backend/app/modules/official_workflows/models.py`
- `backend/tests/test_v8_w1_d3_work_package_evidence_link.py`
- `artifacts/FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Run in the frozen global Alembic order; use SQLite-safe forward-only migration semantics, unique-head check and clean temporary upgrade head.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_w1_d3_work_package_evidence_link.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_d3_work_package_evidence_link.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_d3_work_package_evidence_link.py app/modules/official_workflows/models.py tests/test_v8_w1_d3_work_package_evidence_link.py && .venv/bin/ruff format alembic/versions/v8_w1_d3_work_package_evidence_link.py app/modules/official_workflows/models.py tests/test_v8_w1_d3_work_package_evidence_link.py && .venv/bin/ruff check alembic/versions/v8_w1_d3_work_package_evidence_link.py app/modules/official_workflows/models.py tests/test_v8_w1_d3_work_package_evidence_link.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w1_d3_work_package_evidence_link.py backend/app/modules/official_workflows/models.py backend/tests/test_v8_w1_d3_work_package_evidence_link.py tasks/postdemo/v8/FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
