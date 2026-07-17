# FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01

Status: PASS / INDEPENDENT REVIEW APPROVED 2026-07-14 / ULTRA CONTRACT FROZEN 2026-07-13
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `13. Wave 5 — PayList internal/official/payment boundary`
Catalog ordinal: `159`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md` §6
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

- RED expectation: Exact schema test fails because `PayListExportArtifact` /
  `t_pay_list_export_artifact`, revision `v8_w5_pay_list_export_artifact_01` and the
  frozen 14-column/constraint/index contract are absent.
- GREEN expectation: Exact ORM and migrated-SQLite tests prove the frozen 14 columns,
  types, nullability, defaults, FKs, checks, scoped idempotency unique and lookup index;
  task-scoped Ruff, exact unique-head check and clean temporary SQLite `upgrade head`
  pass.

## Ultra Contract Freeze — 2026-07-13

High must implement exactly the carrier below. This freeze resolves only the physical
schema ambiguity identified by the approved delta §6; it does not authorize a service,
API, seed, UI, workbook adapter, backfill or customer-decision read.

### Frozen migration identity and order

| Item | Exact contract |
| --- | --- |
| migration file | `backend/alembic/versions/v8_w5_pay_list_export_artifact.py` |
| `revision` | `v8_w5_pay_list_export_artifact_01` |
| `down_revision` | `v8_w4_official_rate_book_01` |
| branch / dependency labels | `None` / `None` |
| direction | forward-only; `downgrade()` raises `NotImplementedError("This is a forward-only migration")` |

This task owns the next globally serialized Alembic head immediately after
`v8_w4_official_rate_book_01`. Before RED/source work, High must confirm that revision is
the single head. A different or multiple head is a planning blocker: do not guess a new
`down_revision`, merge heads or branch the migration.

The migration creates only `t_pay_list_export_artifact` and its one explicit index. It
performs no update, delete, backfill, PayList status conversion or seed. An existing
table/column/constraint collision is a failed precheck, not an idempotent success.

### Frozen ORM and table contract

- ORM class: `PayListExportArtifact`.
- Table: `t_pay_list_export_artifact`.
- The class uses `UUIDPrimaryKeyMixin` and `Base`, not `AuditMixin`; the latter would add
  unapproved audit columns and incompatible Python-side timestamp behavior.
- The UUID is `str(uuid4())` generated in application code and stored as SQLite-safe
  `String(36)`. Correctness must not rely on database UUID functions or `RETURNING`.
- No SQLAlchemy relationship, enum class, second table or compatibility column on
  `PayList` is added.

The table has exactly these 14 columns and no others:

| Column | SQLAlchemy / Alembic type | ORM annotation | Nullable | Server default | FK / meaning |
| --- | --- | --- | --- | --- | --- |
| `id` | `String(36)` | `Mapped[str]` | no | none; application UUID | primary key |
| `pay_list_id` | `Integer` | `Mapped[int]` | no | none | owning `t_pay_list.id`; aligned with the existing INTEGER PK |
| `kind` | `String(32)` | `Mapped[str]` | no | none | exactly `INTERNAL_XLSX` or `OFFICIAL_XLSM` |
| `status` | `String(32)` | `Mapped[str]` | no | none | exactly `GENERATED` or `OFFICIAL_SITE_ACCEPTED` |
| `content_sha256` | `String(64)` | `Mapped[str]` | no | none | bare lowercase SHA-256 digest of the stored bytes |
| `managed_storage_path` | `Text` | `Mapped[str]` | no | none | opaque application-managed storage path, not an upload result |
| `template_version` | `String(128)` | `Mapped[str \| None]` | yes | none | required only for `OFFICIAL_XLSM` |
| `generated_by` | `String(36)` | `Mapped[str]` | no | none | generating `t_user.id` actor |
| `generated_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | immutable generation time |
| `idempotency_key` | `String(128)` | `Mapped[str]` | no | none | retry identity scoped to the owning PayList |
| `official_acceptance_evidence_ref` | `String(512)` | `Mapped[str \| None]` | yes | none | official-site acceptance evidence reference |
| `official_acceptance_evidence_hash` | `String(64)` | `Mapped[str \| None]` | yes | none | bare lowercase SHA-256 digest of that evidence |
| `official_accepted_at` | `DateTime(timezone=False)` | `Mapped[datetime \| None]` | yes | none | official-site acceptance time |
| `updated_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | later acceptance writes update it explicitly |

`kind`, `status` and `idempotency_key` have no database or ORM default: a later service
must provide the exact intended facts. `generated_at` and `updated_at` use only
`sa.text("CURRENT_TIMESTAMP")`; `now()` and dialect-specific timestamp functions are
prohibited. The two digest length checks below are carrier checks; exact lowercase-hex
validation belongs to the later writing service.

### Frozen constraints and index

In addition to the repository-default unnamed primary key, the table has exactly these
named constraints:

| Name | Exact contract |
| --- | --- |
| `fk_t_pay_list_export_artifact_pay_list_id` | `pay_list_id -> t_pay_list.id`, `ON DELETE CASCADE` |
| `fk_t_pay_list_export_artifact_generated_by` | `generated_by -> t_user.id`, `ON DELETE RESTRICT` |
| `uq_t_pay_list_export_artifact_pay_list_idempotency_key` | `UNIQUE(pay_list_id, idempotency_key)`; the same key may be used on different PayLists |
| `ck_t_pay_list_export_artifact_kind` | kind vocabulary check below |
| `ck_t_pay_list_export_artifact_status` | status vocabulary check below |
| `ck_t_pay_list_export_artifact_content_sha256` | content digest length check below |
| `ck_t_pay_list_export_artifact_acceptance_hash` | nullable acceptance digest length check below |
| `ck_t_pay_list_export_artifact_kind_payload` | INTERNAL has no template; OFFICIAL requires one |
| `ck_t_pay_list_export_artifact_acceptance_tuple` | GENERATED has no acceptance tuple; accepted OFFICIAL has the complete tuple |

The check expressions are exact:

```sql
kind IN ('INTERNAL_XLSX', 'OFFICIAL_XLSM')
status IN ('GENERATED', 'OFFICIAL_SITE_ACCEPTED')
length(content_sha256) = 64
official_acceptance_evidence_hash IS NULL OR length(official_acceptance_evidence_hash) = 64
(kind = 'INTERNAL_XLSX' AND template_version IS NULL)
OR (kind = 'OFFICIAL_XLSM' AND template_version IS NOT NULL)
(status = 'GENERATED'
 AND official_acceptance_evidence_ref IS NULL
 AND official_acceptance_evidence_hash IS NULL
 AND official_accepted_at IS NULL)
OR (status = 'OFFICIAL_SITE_ACCEPTED'
    AND kind = 'OFFICIAL_XLSM'
    AND official_acceptance_evidence_ref IS NOT NULL
    AND official_acceptance_evidence_hash IS NOT NULL
    AND official_accepted_at IS NOT NULL)
```

The migration and ORM may wrap these expressions only for Python formatting; they must
not add or weaken a branch.

The table has exactly one explicit non-unique index:

`ix_t_pay_list_export_artifact_pay_list_generated_at(pay_list_id, generated_at)`.

There is deliberately no unique constraint or index on `content_sha256`: separate
retries, PayLists or kinds may legitimately produce identical bytes. There is no
`current_identity_key`, current-artifact unique, acceptance ticket unique or managed-path
unique.

### Frozen fact and gate boundary

- `INTERNAL_XLSX` always has `template_version=NULL`, `status=GENERATED` and no official
  acceptance evidence tuple.
- `OFFICIAL_XLSM` always has a non-null `template_version`. While `GENERATED`, it has no
  acceptance tuple; `OFFICIAL_SITE_ACCEPTED` requires ref/hash/time together.
- `OFFICIAL_SITE_ACCEPTED` records only official-site acceptance evidence. It does not
  mean uploaded, paid, reconciled or ticket-verified.
- The carrier contains no `UPLOADED`, `PAID`, ticket, failure/retry outcome,
  supersede/current flag or payment state.
- `DG-PAYMENT-WORKBOOK` is not read by and is not a dependency of this schema task. The
  carrier stores both frozen kinds/statuses. While the gate is unconfirmed, later
  creation services may create only `INTERNAL_XLSX`; they must not create
  `OFFICIAL_XLSM` or an accepted artifact. That service behavior remains outside this
  closure.
- The scoped unique enforces only `(pay_list_id, idempotency_key)`. Exact replay versus
  payload-conflict behavior and any status transition are owned by later services.

### Exact RED / GREEN schema assertions

The exact schema test must prove:

1. RED fails because the ORM class, table and frozen revision are absent.
2. ORM metadata and reflected clean-upgraded SQLite contain exactly the 14 columns above
   with matching types, nullability and `CURRENT_TIMESTAMP` defaults.
3. The revision/down-revision, both named FKs, all six named CHECKs, the scoped unique
   and the one explicit non-unique index match exactly; Alembic has the single head
   `v8_w5_pay_list_export_artifact_01`.
4. An application UUID exists and survives `flush()` without relying on `RETURNING`;
   valid INTERNAL generated, OFFICIAL generated and OFFICIAL accepted rows succeed with
   SQLite foreign keys enabled.
5. Invalid kind/status, 63-character content or acceptance hashes, INTERNAL template or
   acceptance facts, OFFICIAL without a template, GENERATED with any acceptance fact,
   and accepted rows missing any ref/hash/time fail.
6. Equal `(pay_list_id, idempotency_key)` values fail, while the same key on two PayLists
   succeeds. Repeated `content_sha256` values succeed and no content/current uniqueness
   exists.
7. Missing PayList or generating user FKs fail; deletion behavior matches the frozen
   CASCADE/RESTRICT actions.
8. A clean temporary SQLite `upgrade head` reaches exactly
   `v8_w5_pay_list_export_artifact_01 (head)` without backfill or a second head.

## Exact Closure Slice

Add only the frozen 14-column `PayListExportArtifact` /
`t_pay_list_export_artifact` carrier with the exact PayList/user FKs, kind/status/hash and
acceptance checks, PayList-scoped idempotency unique and PayList/generation-time index.

## Explicit Non-Closure

No backfill, service, API/endpoint, seed, UI, gate read, workbook generation, acceptance
transition or second table/carrier. Do not absorb another V8 catalog row, a second
closure slice, an unresolved customer policy or unrelated cleanup.

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
- Run only after the frozen `v8_w4_official_rate_book_01` head and under the
  `GLOBAL_ALEMBIC_HEAD` lock; use SQLite-safe forward-only migration semantics, aligned
  INTEGER FK types, unique-head verification and a clean temporary upgrade.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_pay_list_export_artifact_schema.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_pay_list_export_artifact_schema.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w5_pay_list_export_artifact.py app/modules/annuity/models.py tests/test_v8_pay_list_export_artifact_schema.py && .venv/bin/ruff format alembic/versions/v8_w5_pay_list_export_artifact.py app/modules/annuity/models.py tests/test_v8_pay_list_export_artifact_schema.py && .venv/bin/ruff check alembic/versions/v8_w5_pay_list_export_artifact.py app/modules/annuity/models.py tests/test_v8_pay_list_export_artifact_schema.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads  # exact output: v8_w5_pay_list_export_artifact_01 (head)`
- `cd backend && tmp_dir="$(mktemp -d)" && DATABASE_URL="sqlite:///${tmp_dir}/pay-list-export-artifact.db" PYTHONPATH=. .venv/bin/alembic upgrade head && DATABASE_URL="sqlite:///${tmp_dir}/pay-list-export-artifact.db" PYTHONPATH=. .venv/bin/alembic current  # isolated clean SQLite; exact current: v8_w5_pay_list_export_artifact_01 (head)`
- `git diff --check -- backend/alembic/versions/v8_w5_pay_list_export_artifact.py backend/app/modules/annuity/models.py backend/tests/test_v8_pay_list_export_artifact_schema.py tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
