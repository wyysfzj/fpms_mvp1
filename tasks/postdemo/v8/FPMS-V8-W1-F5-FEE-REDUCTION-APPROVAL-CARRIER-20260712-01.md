# FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `8. Wave 1 — schema spine, globally serialized`
Catalog ordinal: `13`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `362`
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

- RED expectation: The exact schema test requires revision `v8_w1_f5_fee_reduction_01` over `v8_w1_f4_payment_link_01` and the frozen 22-column `FeeReductionApproval` / `t_fee_reduction_approval` carrier, but fails before implementation because the model/table is absent.
- GREEN expectation: The exact 22-column ORM/migrated schema, two named FKs, scope-exclusivity CHECK and unique `approval_identity_key` pass their SQLite behavior checks; task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` also pass.

## Exact Closure Slice

Add only the frozen 22-column `FeeReductionApproval` / `t_fee_reduction_approval` deterministic CASE/APPLICANT_SET approval source/scope/snapshot/interval carrier, its exact scope-exclusivity CHECK, source/case FKs and SQLite-safe unique approval identity.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Replan Record — 2026-07-13

- Blocker found before RED/source edits: the canonical design and plan froze the conceptual approval carrier but not its physical column names, types, nullability, defaults, SQLite identity representation or exact constraint names.
- Resolution: the physical contract below is frozen from canonical V8 schema section 5.3, the approved fee-reduction semantics and existing SQLite-safe `Numeric`/`Text`/timestamp conventions. The closure slice remains one table/carrier; no service rule or second carrier is absorbed.
- Story Shape Classification remains unchanged: the globally serialized Alembic chain and shared fee model keep schema/evidence cost high.
- `chosen_runbook` remains `P0-prereq-heavy-story`.
- Implementation may start only after F4 is PASS and the unique Alembic head is exactly `v8_w1_f4_payment_link_01`; a mismatch returns to planning rather than creating a branch.

## Frozen Physical Schema Contract

ORM class and table:

- Class: `FeeReductionApproval`
- Table: `t_fee_reduction_approval`
- Migration revision: `v8_w1_f5_fee_reduction_01`
- Migration `down_revision`: `v8_w1_f4_payment_link_01`
- Migration policy: forward-only; `downgrade()` raises `NotImplementedError`.

The table has exactly these 22 columns:

| Column | SQLAlchemy / Alembic type | ORM annotation | Nullable | Server default | Meaning |
| --- | --- | --- | --- | --- | --- |
| `id` | `String(36)` | `Mapped[str]` | no | none; application UUID | approval identity |
| `scope_type` | `String(32)` | `Mapped[str]` | no | none | physical discriminator; database CHECK permits only `CASE` or `APPLICANT_SET` |
| `case_id` | `String(36)` | `Mapped[str \| None]` | yes | none | CASE scope owner; mutually exclusive with `applicant_set_key` |
| `applicant_set_key` | `String(64)` | `Mapped[str \| None]` | yes | none | APPLICANT_SET SHA-256 key; mutually exclusive with `case_id` |
| `reduction_ratio` | `Numeric(5, 4)` | `Mapped[Decimal]` | no | none | official reduction ratio, not payable ratio |
| `fee_scope_snapshot` | `Text` | `Mapped[str]` | no | none | canonical Text-JSON snapshot of the official fee-code scope |
| `fee_scope_hash` | `String(64)` | `Mapped[str]` | no | none | SHA-256 of the canonical fee-scope snapshot |
| `fee_year_from` | `Integer` | `Mapped[int \| None]` | yes | none | inclusive first applicable fee year; null for a non-annual scope |
| `fee_year_to` | `Integer` | `Mapped[int \| None]` | yes | none | inclusive last applicable fee year; null for a non-annual scope |
| `effective_from` | `Date` | `Mapped[date]` | no | none | source-backed first effective date |
| `effective_to` | `Date` | `Mapped[date \| None]` | yes | none | optional inclusive end date; null means source-backed open end |
| `source_evidence_version_id` | `String(36)` | `Mapped[str]` | no | none | immutable document-evidence version that proves the approval |
| `confirmation_status` | `String(32)` | `Mapped[str]` | no | none | explicit approval confirmation state |
| `confirmed_at` | `DateTime(timezone=False)` | `Mapped[datetime \| None]` | yes | none | confirmation decision time |
| `confirmed_by` | `String(36)` | `Mapped[str \| None]` | yes | none | confirming actor snapshot; no user FK |
| `eligibility_snapshot` | `Text` | `Mapped[str]` | no | none | retained versioned Text-JSON eligibility/applicant snapshot |
| `eligibility_snapshot_hash` | `String(64)` | `Mapped[str]` | no | none | SHA-256 of the canonical eligibility snapshot |
| `approval_identity_key` | `String(64)` | `Mapped[str]` | no | none | service-computed SHA-256 source/scope/ratio/fee/year/effective identity |
| `created_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | audit creation time |
| `updated_at` | `DateTime(timezone=False)` | `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | audit update time; later writes update it explicitly |
| `created_by` | `String(36)` | `Mapped[str \| None]` | yes | none | audit creator snapshot; no user FK |
| `updated_by` | `String(36)` | `Mapped[str \| None]` | yes | none | audit updater snapshot; no user FK |

Exact named keys and constraints:

| Name | Contract |
| --- | --- |
| primary key | `PRIMARY KEY (id)` |
| `fk_t_fee_reduction_approval_case_id` | nullable `case_id -> t_case.id`, `ON DELETE CASCADE` |
| `fk_t_fee_reduction_approval_source_evidence_version_id` | `source_evidence_version_id -> t_document_evidence_version.id`, default `NO ACTION` |
| `ck_t_fee_reduction_approval_scope_exclusive` | `(scope_type = 'CASE' AND case_id IS NOT NULL AND applicant_set_key IS NULL) OR (scope_type = 'APPLICANT_SET' AND case_id IS NULL AND applicant_set_key IS NOT NULL)` |
| `uq_t_fee_reduction_approval_identity_key` | `UNIQUE (approval_identity_key)` |

### Database identity versus service canonicalization

- `approval_identity_key` is the database representation of the approved unique source/scope/ratio/interval identity. The later record service computes SHA-256 over the delimiter-safe canonical encoding of: `source_evidence_version_id`, `scope_type`, the non-null scope identifier, reduction ratio normalized to four decimal places, `fee_scope_hash`, nullable fee-year bounds, `effective_from` and nullable `effective_to`.
- A dedicated non-null identity key is required because SQLite treats NULL values in a multi-column UNIQUE constraint as distinct. A raw composite containing nullable CASE/APPLICANT_SET and interval columns would not prevent duplicate approvals.
- The database CHECK owns only the exact scope discriminator/exclusivity invariant. It does not compute or validate `applicant_set_key`, `fee_scope_hash`, `eligibility_snapshot_hash` or `approval_identity_key`.
- The later approval-record service owns sorted/distinct applicant IDs, the versioned eligibility-attribute snapshot, delimiter-safe hashing, Text-JSON canonicalization, hash/snapshot conflict detection, fee/year/date interval validation and idempotent reuse.
- The later validator owns the business vocabulary `0`, `0.7`, `0.85`, confirmed/current applicability and payable-ratio conversion. F5 adds no ratio CHECK or implicit default.

Frozen invariants and exclusions:

- `source_evidence_version_id`, both snapshots/hashes, reduction ratio, effective start and identity key are mandatory; the carrier cannot manufacture or silently omit approval evidence.
- Both scope modes retain an eligibility snapshot. APPLICANT_SET additionally requires `applicant_set_key` through the exact database CHECK; CASE additionally requires `case_id` through the same CHECK.
- The simple evidence-version FK proves source existence. Same-case/source applicability and APPLICANT_SET reuse are service invariants; F5 does not alter `t_document_evidence_version` to add another composite parent key.
- No server default exists for business fields or confirmation. No status, ratio, year-order, effective-order, digest-length or JSON-shape CHECK is added beyond the exact scope CHECK.
- Do not use `AuditMixin`: its Python-side timestamp behavior does not satisfy the frozen migration-level `CURRENT_TIMESTAMP` contract.
- No source document duplicate, obligation FK, amount, payable ratio, rate-book link, current-row flag, supersede fields, secondary index or extra UNIQUE is authorized.

## Frozen RED / GREEN Contract

- RED must require `FeeReductionApproval` / `t_fee_reduction_approval`, the exact 22 columns, types, nullability/defaults and four named constraints above; before implementation it fails because the model/table is absent.
- GREEN must prove ORM and migrated SQLite metadata match exactly, application-generated UUID IDs work after `flush()`, valid CASE and APPLICANT_SET rows are accepted, mixed/missing/unknown scope combinations are rejected, missing case/source-evidence references are rejected with foreign keys enabled, and duplicate non-null `approval_identity_key` values are rejected even when interval/scope columns contain NULL.
- GREEN must prove business columns have no server defaults, no unapproved ratio/interval CHECK exists, and no second carrier is created.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01`
- `FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): F1

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `11`; project this order only across owners present in the active manifest.
- `backend/app/modules/fees/models.py` order key `5`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w1_f5_fee_reduction_approval.py`
- `backend/app/modules/fees/models.py`
- `backend/tests/test_v8_w1_f5_fee_reduction_approval.py`
- `artifacts/FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Run in the frozen global Alembic order; use SQLite-safe forward-only migration semantics, unique-head check and clean temporary upgrade head.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f5_fee_reduction_approval.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f5_fee_reduction_approval.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w1_f5_fee_reduction_approval.py app/modules/fees/models.py tests/test_v8_w1_f5_fee_reduction_approval.py && .venv/bin/ruff format alembic/versions/v8_w1_f5_fee_reduction_approval.py app/modules/fees/models.py tests/test_v8_w1_f5_fee_reduction_approval.py && .venv/bin/ruff check alembic/versions/v8_w1_f5_fee_reduction_approval.py app/modules/fees/models.py tests/test_v8_w1_f5_fee_reduction_approval.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w1_f5_fee_reduction_approval.py backend/app/modules/fees/models.py backend/tests/test_v8_w1_f5_fee_reduction_approval.py tasks/postdemo/v8/FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
