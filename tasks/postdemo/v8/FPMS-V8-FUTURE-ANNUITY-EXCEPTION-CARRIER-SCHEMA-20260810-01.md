# FPMS-V8-FUTURE-ANNUITY-EXCEPTION-CARRIER-SCHEMA-20260810-01

Status: FROZEN CANDIDATE / READY FOR INDEPENDENT HIGH REVIEW
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates / future-annuity prerequisite`
Executor role: Backend Developer / worker
Repository risk: HIGH

## Design References

- `AGENTS.md`
- `docs/product/v8/domain-contract.md`
- `docs/product/v8/source-decision-registry.md`
- `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`
- `docs/product/v8/reviews/V8-FULL-BATCH-CUSTOMER-DECISION-CURRENT-ADOPTION.md`
- `tasks/batches/FPMS-POSTDEMO-V8-FUTURE-ANNUITY-GATE-20260712-01.md`
- `docs/product/v8/reviews/V8-FUTURE-ANNUITY-GATE-MANIFEST-ACTIVATION-CURRENT-ADOPTION.md`
- Blocked consumer:
  `tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-AUTO-DRAFT-POLICY-20260712-01.md`
- Customer gate requirement: `DG-FEE-FUTURE-ANNUITY[GLOBAL]`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SCHEMA`

- RED expectation: the focused schema test fails because the named ORM carrier, table,
  constraints, foreign keys, indexes or frozen migration do not exist.
- GREEN expectation: exact ORM/reflected-SQLite parity, database constraint behavior, ORM
  append-only guards, one Alembic head and a clean isolated SQLite `upgrade head` pass while the
  new table remains empty.

## Why this prerequisite is mandatory

Scheme A keeps client instruction as the default prerequisite for a future-annuity draft and
starts with no exception. A later exception requires institution-administrator publication for
one exact customer or case, an explicit start and end, unique version, content hash, confirming
actor, publication/effective times and retained audit.

The existing `t_customer_decision_gate` is only the source-backed `GLOBAL` policy gate. It accepts
`GLOBAL` or `case:*`, has only one `effective_at`, treats non-legacy `decision_value` as an
untyped non-empty string, and has no customer scope, explicit end, exception content hash or
exception-use lineage. Encoding an exception as ad hoc JSON in that table is prohibited.

This prerequisite therefore adds exactly one append-only publication/revocation record table. It
does not publish an exception, resolve one, expose an endpoint, create a draft or change the
default instruction rule.

## Exact Closure Slice

Create one SQLite-safe forward-only migration, one exact ORM carrier and one focused schema test
for append-only future-annuity draft-exception `PUBLISHED` and `REVOKED` records. Freeze every
column, constraint, foreign key, index and immutable ORM boundary below. Insert no row.

## Frozen policy and time boundary

- `DG-FEE-FUTURE-ANNUITY:GLOBAL` remains the separate mandatory global policy gate. This table is
  not a replacement gate and cannot activate itself.
- An empty table is the only initial/default state and means no exception. It never means a
  wildcard or permissive fallback.
- A published exception has exactly one `CLIENT` or `CASE` scope. No `GLOBAL`, department, user,
  role, wildcard or composite scope is represented.
- Applicability is the half-open UTC-naive interval `[effective_from, effective_to)`.
  `effective_to` is mandatory and strictly later than `effective_from`.
- `published_at` is the later service's server-captured publication time; `effective_at` is the
  record's separately retained authorization-effect time; `effective_from/effective_to` are the
  separately retained applicability interval. This schema records all three time facts but does
  not infer or enforce equality or ordering between publication time, effect time and interval
  start. Only `effective_to > effective_from` is frozen here.
- Publication and revocation are separate append-only rows. Revocation never updates or deletes
  its target publication and never rewrites a historical draft or activity.
- The database stores exact snapshot text and hash. Canonical JSON construction, hash
  recomputation, authorization, overlap detection, target-state validation and resolution belong
  to later services and do not enter this schema task.

## Frozen migration identity and precheck

| Item | Exact contract |
| --- | --- |
| migration file | `backend/alembic/versions/v8_future_annuity_exception_carrier.py` |
| `revision` | `v8_future_annuity_exception_01` |
| `down_revision` | `v8_grant_source_carrier_01` |
| branch / dependency labels | `None` / `None` |
| direction | forward-only; `downgrade()` raises `NotImplementedError("This is a forward-only migration")` |

The post-grant-source re-freeze precheck observed exactly one accepted Alembic head,
`v8_grant_source_carrier_01`. Before implementation, the worker must re-run:

`cd backend && PYTHONPATH=. .venv/bin/alembic heads`

If the result is not exactly `v8_grant_source_carrier_01 (head)`, or the frozen revision, table,
class, constraint or index name already exists, stop only this lane and return the task for
migration-order re-freeze. Do not guess a new `down_revision`, create a merge revision, rebase
another schema task into this ownership or silently skip a collision.

The migration uses only SQLite-safe `op.create_table` and `op.create_index`. It performs no alter,
backfill, update, delete, seed, decision-gate write, exception publication or status coercion.
Correctness must not depend on `RETURNING` or a PostgreSQL-only type/function.

## Frozen ORM ownership

- ORM class: `FutureAnnuityDraftExceptionRecord`.
- ORM file: `backend/app/modules/system/models.py`.
- Table: `t_future_annuity_draft_exception_record`.
- Use explicit mapped columns, application UUIDs from `str(uuid4())`,
  `DateTime(timezone=False)` and explicit `CURRENT_TIMESTAMP` only where specified below.
- Do not add a relationship property, enum module, repository abstraction, mixin, second table or
  compatibility column on an existing table.
- Add exact `before_update` and `before_delete` ORM listeners that raise
  `ValueError("future annuity draft exception record is append-only")`. Later services append a
  successor/revocation record; they never mutate or delete one.
- ORM metadata and migration must match exactly.

## Physical schema — `t_future_annuity_draft_exception_record`

The table has exactly these 19 columns and no others:

| Column | SQLAlchemy / ORM type | Nullable | Server default | Exact meaning |
| --- | --- | --- | --- | --- |
| `id` | `String(36)` / `Mapped[str]` | no | none | application UUID primary key |
| `record_type` | `String(16)` / `Mapped[str]` | no | none | `PUBLISHED` or `REVOKED` |
| `scope_type` | `String(16)` / `Mapped[str \| None]` | yes | none | `CLIENT` or `CASE` only on publication |
| `client_id` | `String(36)` / `Mapped[str \| None]` | yes | none | exact customer scope only on `CLIENT` publication |
| `case_id` | `String(36)` / `Mapped[str \| None]` | yes | none | exact case scope only on `CASE` publication |
| `effective_from` | `DateTime(timezone=False)` / `Mapped[datetime \| None]` | yes | none | inclusive publication interval start |
| `effective_to` | `DateTime(timezone=False)` / `Mapped[datetime \| None]` | yes | none | exclusive mandatory publication interval end |
| `target_publication_id` | `String(36)` / `Mapped[str \| None]` | yes | none | exact publication targeted only by `REVOKED` |
| `record_version` | `String(128)` / `Mapped[str]` | no | none | globally unique immutable publication/revocation version |
| `source_reference` | `String(512)` / `Mapped[str]` | no | none | exact authority/source reference retained by the record |
| `source_version` | `String(128)` / `Mapped[str]` | no | none | exact authority/source version retained by the record |
| `reason` | `Text` / `Mapped[str]` | no | none | retained publication or revocation reason |
| `record_snapshot` | `Text` / `Mapped[str]` | no | none | immutable canonical JSON record |
| `record_snapshot_hash` | `String(64)` / `Mapped[str]` | no | none | lowercase SHA-256 hex of exact snapshot text |
| `confirmed_by` | `String(36)` / `Mapped[str]` | no | none | authenticated confirming institution actor |
| `published_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | none | server-captured publication time |
| `effective_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | none | publication/revocation effect time |
| `idempotency_key` | `String(128)` / `Mapped[str]` | no | none | immutable record replay identity |
| `created_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | database insertion audit time |

## Exact identities, constraints and foreign keys

In addition to the primary key, the table has exactly these named unique constraints:

- `uq_t_future_annuity_draft_exception_record_version` is `UNIQUE(record_version)`.
- `uq_t_future_annuity_draft_exception_idempotency_key` is `UNIQUE(idempotency_key)`.
- `uq_t_future_annuity_draft_exception_target_publication_id` is
  `UNIQUE(target_publication_id)`; SQLite permits multiple `NULL` publication values while an
  exact publication can be targeted by at most one revocation row.

It has exactly these foreign keys, all `ON DELETE RESTRICT`:

- `fk_t_future_annuity_draft_exception_client_id`: `client_id -> t_client.id`.
- `fk_t_future_annuity_draft_exception_case_id`: `case_id -> t_case.id`.
- `fk_t_future_annuity_draft_exception_target_id`:
  `target_publication_id -> t_future_annuity_draft_exception_record.id`.
- `fk_t_future_annuity_draft_exception_confirmed_by`: `confirmed_by -> t_user.id`.

It has exactly these named check constraints:

- `ck_t_future_annuity_draft_exception_record_type`:
  `record_type IN ('PUBLISHED', 'REVOKED')`.
- `ck_t_future_annuity_draft_exception_hash` requires exactly 64 lowercase hexadecimal
  characters:
  `length(record_snapshot_hash) = 64 AND record_snapshot_hash = lower(record_snapshot_hash) AND record_snapshot_hash NOT GLOB '*[^0-9a-f]*'`.
- `ck_t_future_annuity_draft_exception_shape` permits exactly one of these shapes:
  - `PUBLISHED`: `target_publication_id IS NULL`; `scope_type` is `CLIENT` or `CASE`;
    `effective_from` and `effective_to` are non-null; `effective_to > effective_from`;
    and the scope tuple is exact XOR: `CLIENT` has non-null `client_id` and null `case_id`, while
    `CASE` has null `client_id` and non-null `case_id`.
  - `REVOKED`: `target_publication_id IS NOT NULL`; `scope_type`, `client_id`, `case_id`,
    `effective_from` and `effective_to` are all null.

The migration and ORM may wrap the check expressions for Python formatting only. They must not
weaken a condition, add another state or use an application-only assertion in place of a database
constraint.

The self-FK and unique target together enforce an existing target and at most one revocation row
per publication. They cannot prove that `target_publication_id` names a `PUBLISHED` row or that a
revocation matches the target's source/scope. The later publication service must prove those facts
before append and the later resolver must revalidate them before use.

## Exact indexes

Create exactly these three non-unique indexes after the table exists:

- `ix_t_future_annuity_draft_exception_client_interval` on
  `(client_id, record_type, effective_from, effective_to, effective_at)`.
- `ix_t_future_annuity_draft_exception_case_interval` on
  `(case_id, record_type, effective_from, effective_to, effective_at)`.
- `ix_t_future_annuity_draft_exception_target` on
  `(target_publication_id, record_type, effective_at)`.

No range-exclusion constraint is invented. SQLite cannot enforce cross-row interval exclusion;
the later service must reject same-scope overlap and customer/case cross-scope ambiguity, and the
later resolver must independently fail closed if corrupted or concurrent rows remain ambiguous.

## Frozen snapshot contract for later services

This task stores snapshot text/hash only and inserts no snapshot. The later service must serialize
UTF-8 canonical JSON with `ensure_ascii=False`, `sort_keys=True`,
`separators=(",", ":")`, `allow_nan=False`, then compute the lowercase SHA-256 hex of the exact
UTF-8 bytes.

The `PUBLISHED` snapshot has exactly these keys:

`schema`, `record_type`, `scope_type`, `scope_id`, `effective_from`, `effective_to`,
`effective_at`, `record_version`, `source_reference`, `source_version`, `reason`, `confirmed_by`,
`published_at`.

The `REVOKED` snapshot has exactly these keys:

`schema`, `record_type`, `target_publication_id`, `effective_at`, `record_version`,
`source_reference`, `source_version`, `reason`, `confirmed_by`, `published_at`.

`schema` is exactly `FPMS_FUTURE_ANNUITY_DRAFT_EXCEPTION_V1`; record type is exact uppercase;
timestamps use timezone-naive UTC ISO-8601 with microseconds. The later service, not this schema
task, validates canonical bytes, recomputes the hash and proves every cross-row fact.

## Focused schema test contract

`backend/tests/test_v8_future_annuity_exception_carrier_schema.py` must prove all and only the
following:

1. The exact ORM class/table/19-column order, mapped types, nullability and server default match
   this contract.
2. Reflected SQLite metadata matches the ORM for every column, named unique/check/FK constraint
   and exact index column order.
3. One valid client-scoped and one valid case-scoped `PUBLISHED` row insert when their referenced
   user/client/case rows exist. Their independently chosen `published_at`, `effective_at` and
   `effective_from` values persist exactly without an equality or cross-field ordering rule.
4. One valid `REVOKED` row inserts only after its referenced publication exists.
5. Invalid record type, invalid hash, missing/dual/wrong scope tuple, missing or inverted interval,
   publication with target, and revocation with publication fields fail at the database boundary.
6. Duplicate `record_version`, duplicate `idempotency_key` and a second `REVOKED` row targeting
   the same publication fail independently at the database boundary.
7. Missing user/client/case/target references and deletion of a referenced user/client/case/target
   fail with SQLite foreign keys enabled.
8. ORM update and delete attempts raise the exact append-only `ValueError`; appending a revocation
   leaves the target publication bytes unchanged.
9. Migration revision/down-revision/forward-only downgrade and ORM/migration names are exact.
10. A clean isolated `upgrade head` creates the table with zero rows and leaves exactly one head.

The test does not call a publication/resolution service, endpoint, draft writer, instruction
writer, payment writer, seed or production database.

## Dependencies and serialization

- Current accepted Scheme A source/adoption, future-annuity gate-manifest activation and
  `V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-CURRENT-ADOPTION` must remain reachable.
- The global migration owner `GLOBAL_ALEMBIC_HEAD`,
  `backend/app/modules/system/models.py` owner and all SQLite-writing verification are serialized.
- This task may not run concurrently with the grant-source carrier or any other migration/model
  owner. Re-run the head and dirty-scope precheck only after acquiring those owners.
- A changed head, shared-file dirt or named-object collision blocks this task until explicit
  re-freeze; it is not authorization to absorb the competing work.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-EXCEPTION-CARRIER-SCHEMA-20260810-01.md`
- `backend/alembic/versions/v8_future_annuity_exception_carrier.py`
- `backend/app/modules/system/models.py`
- `backend/tests/test_v8_future_annuity_exception_carrier_schema.py`
- `artifacts/FPMS-V8-FUTURE-ANNUITY-EXCEPTION-CARRIER-SCHEMA-20260810-01/**`

No other source, model export, migration, schema, service, API, permission, test, task, manifest,
catalog or ledger file is authorized. Preserve the initial tracked/untracked dirty baseline and
record every outside-dirty path without absorbing it.

## Explicit Non-Closure

- No seed, bootstrap row, sample row, default exception, `GLOBAL` exception, open-ended exception
  or production configuration.
- No decision-gate record/value/schema/read-service change.
- No exception publication, revocation, resolver, overlap policy, authorization check, permission,
  API, response schema, UI or exception-use activity.
- No future-annuity obligation, instruction, draft, fee amount, reduction, deadline, PayList,
  GovPayment, payment, receipt or legal/lifecycle state behavior.
- No application-fee or grant-year draft policy and no change to the deep `prepare_draft` rule.
- No second table, compatibility column, relationship, generic abstraction, adjacent refactor,
  catalog/coverage-ledger edit, broad suite, release gate, commit or push.

## Remaining Follow-Up Task IDs

- `FPMS-V8-FUTURE-ANNUITY-EXCEPTION-PUBLICATION-SERVICE-20260810-01`
- `FPMS-V8-FUTURE-ANNUITY-EXCEPTION-API-20260810-01`
- `FPMS-V8-FUTURE-ANNUITY-DRAFT-AUTHORIZATION-SEPARATION-20260810-01`
- `FPMS-V8-FUTURE-ANNUITY-AUTO-DRAFT-POLICY-20260712-01` dependency re-freeze

## Verification Commands

- Preflight before RED:
  `cd backend && PYTHONPATH=. .venv/bin/alembic heads`
  — exact output before implementation must be `v8_grant_source_carrier_01 (head)`.
- RED:
  `cd backend && .venv/bin/pytest -q tests/test_v8_future_annuity_exception_carrier_schema.py`
  — preserve the expected missing-carrier failure before implementation.
- GREEN:
  `cd backend && .venv/bin/pytest -q tests/test_v8_future_annuity_exception_carrier_schema.py`.
- Scoped formatting/lint, only after task-owned edits:
  `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_future_annuity_exception_carrier.py app/modules/system/models.py tests/test_v8_future_annuity_exception_carrier_schema.py && .venv/bin/ruff format alembic/versions/v8_future_annuity_exception_carrier.py app/modules/system/models.py tests/test_v8_future_annuity_exception_carrier_schema.py && .venv/bin/ruff check alembic/versions/v8_future_annuity_exception_carrier.py app/modules/system/models.py tests/test_v8_future_annuity_exception_carrier_schema.py`.
- Unique head after implementation:
  `cd backend && PYTHONPATH=. .venv/bin/alembic heads`
  — exact output must be `v8_future_annuity_exception_01 (head)`.
- Clean isolated SQLite migration, under the global SQLite queue:
  `cd backend && tmp_dir="$(mktemp -d)" && DATABASE_URL="sqlite:///${tmp_dir}/future-annuity-exception-carrier.db" PYTHONPATH=. .venv/bin/alembic upgrade head && DATABASE_URL="sqlite:///${tmp_dir}/future-annuity-exception-carrier.db" PYTHONPATH=. .venv/bin/alembic current`
  — exact current revision must be `v8_future_annuity_exception_01 (head)`.
- Scope/whitespace:
  `git diff --check -- backend/alembic/versions/v8_future_annuity_exception_carrier.py backend/app/modules/system/models.py backend/tests/test_v8_future_annuity_exception_carrier_schema.py tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-EXCEPTION-CARRIER-SCHEMA-20260810-01.md`.
- Task gate, only after the final independent HIGH zero-finding review:
  `./scripts/task_validate.sh FPMS-V8-FUTURE-ANNUITY-EXCEPTION-CARRIER-SCHEMA-20260810-01`.
- Atomic evidence validation, only after the successful task gate is recorded:
  `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FUTURE-ANNUITY-EXCEPTION-CARRIER-SCHEMA-20260810-01 --required-step lint --required-step test --required-step independent_review --required-step scope --required-step task_gate`.

Do not run repo-wide tests, a broad frontend/backend build, broad Playwright, seed, production DB
upgrade, Foundation/Full/Final close or release gate.

## Evidence Path

Evidence path:
`artifacts/FPMS-V8-FUTURE-ANNUITY-EXCEPTION-CARRIER-SCHEMA-20260810-01/**`.

The implementation bundle must retain:

- exact task file hash and implementation HEAD;
- initial tracked/untracked status and outside-dirty paths;
- RED log with the expected missing-carrier failure;
- GREEN, scoped Ruff, unique-head and clean temporary SQLite upgrade/current logs;
- baseline-subtracted allowlist patch and patch SHA-256;
- scope report proving no file outside the allowlist was absorbed;
- independent HIGH review binding the exact patch hash, with one final
  `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`;
- latest successful `lint`, `test`, `scope`, `independent_review`, `task_gate` and
  `atomic_evidence` results, with command logs and zero return codes.

Historical receipts or a review of different bytes do not close this task. The implementer cannot
self-approve. A later migration-head change invalidates this task's head-dependent verification
and requires re-freeze/reverification without recapturing unrelated dirt.

## Acceptance and adoption order

1. Independently review and adopt this exact task-contract file. Contract review does not
   implement or approve the schema.
2. Insert this prerequisite into the future-annuity lane before any exception service/API or the
   blocked auto-draft consumer; changed manifest bytes require their own independent adoption.
3. Acquire the Alembic, system-model and SQLite owners; re-run the head/dirt/collision precheck.
4. Preserve RED, implement only the migration/ORM/focused test, run the scoped checks and obtain
   independent HIGH zero-finding review.
5. Only after current acceptance may the publication service task start. The API, deep draft
   authorization separation and auto-draft consumer remain separately owned successors.

## Done Definition

The exact RED is preserved; the minimum allowlisted migration/ORM/test makes the focused GREEN,
ORM/reflected parity, append-only guards, unique-head and clean isolated SQLite upgrade pass;
scoped Ruff/diff and dirty-baseline evidence are current; the table contains no row; no second
closure is absorbed; an independent HIGH reviewer approves the exact patch with zero P0/P1/P2
findings; and the latest `task_gate` and `atomic_evidence` results both PASS. Only then may the
implementation task be reported PASS.

This contract-materialization turn edits only this task file and is reported
`TASK_CONTRACT_READY`, never schema PASS.
