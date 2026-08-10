# FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SCHEMA-20260810-01

Status: FROZEN CANDIDATE / READY FOR INDEPENDENT HIGH REVIEW
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates / grant manual-review prerequisite`
Executor role: Backend Developer / worker
Risk class: `PROTECTED`

## Authority and design references

- `AGENTS.md`
- `docs/product/v8/domain-contract.md`
- `docs/product/v8/source-decision-registry.md`
- `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`
- `docs/product/v8/reviews/V8-FULL-BATCH-CUSTOMER-DECISION-CURRENT-ADOPTION.md`
- `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01.md`
- `tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-EXCEPTION-CARRIER-SCHEMA-20260810-01.md`
- Blocked consumers:
  - `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01.md`
  - `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-REVIEW-SERVICE-20260712-01.md`
- Customer gate requirement: `DG-GRANT-MANUAL-REVIEW[GLOBAL]`.

Frozen customer authority:

- Decision: Scheme A, `APPROVED_POLICY / CONFIG_REQUIRED`.
- Exact decision version:
  `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`.
- Exact source size: `2167` bytes.
- Exact source SHA-256:
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Exact policy: an institution administrator configures the official-copy acquisition role, first
  verification role, second verification role, controlled manual-review proposal role and manual-
  review second-review role. Missing, stale or incomplete role/personnel binding is `409 / NO
  WRITE / NO LEGAL-STATE CHANGE`. First and second verifiers must be different actual users;
  proposer and second reviewer must be different actual users.

## Story shape and task profile

- `shared_file_density`: high
- `prerequisite_density`: high
- `backend_frontend_coupling`: low
- `verification_cost`: high
- Chosen runbook: `P0-prereq-heavy-story`
- Task Contract Profile: `TC-SCHEMA`

RED expectation: the focused schema test fails because the exact role-configuration ORM carrier,
table, migration, registry export, constraints, foreign keys or index is absent.

GREEN expectation: ORM/reflected-SQLite parity, exact constraint/FK/index behavior, fresh standard
model bootstrap, one Alembic head and a clean isolated SQLite `upgrade head` pass while the new
table contains zero rows.

## Why a dedicated carrier is mandatory

Reuse the existing RBAC identities and live bindings:

- `t_role` is the stable identity of each configured institutional role.
- `t_user_role` remains the live user-to-role membership carrier.
- `t_user.is_active` remains the live personnel-eligibility fact.
- Existing permissions remain endpoint permissions; they are not institutional duty-slot values.

None of the existing configuration stores may replace this carrier:

- `t_customer_decision_gate` records the approved policy and its authority, not the concrete five-
  role publication.
- `t_system_param` is mutable key/value state and has no immutable version/hash, predecessor chain,
  effective interval or fail-closed current publication identity.
- `t_role_perm` maps endpoint permissions and cannot distinguish the five approved duties.
- `t_grant_evidence_source_config` selects an official source per evidence scope; overloading it
  would merge the independently approved source and manual-review gates.
- `t_grant_evidence_candidate` is operational evidence/proposal history, not institution
  configuration, and does not carry the first/second official-copy verification pair.

The minimum durable configuration is therefore exactly one fixed-shape table with five non-null
foreign keys to existing roles. A generic child-binding table is not added: the approved slot set is
closed and fixed, and a child table would permit incomplete publications that require count-based
interpretation. No new role, user, user-role membership or permission row is created.

## Exact closure slice

Create one SQLite-safe forward-only migration, one exact ORM carrier, one standard model-registry
import/export and one focused schema test for a versioned `GLOBAL` grant manual-review role
configuration. The carrier stores complete `ACTIVE` or `REVOKED` publications, their five role
identities, immutable canonical snapshot/hash, confirming actor, publication/effective times,
predecessor/current identities and insertion/current-pointer audit times. Insert no row.

## Fail-closed role and time boundary

- Gate/scope are exactly `DG-GRANT-MANUAL-REVIEW` / `GLOBAL`. There is no customer, case,
  department, evidence-scope, user, wildcard or fallback configuration.
- All five role IDs are mandatory on every `ACTIVE` or `REVOKED` publication. A revoked successor
  copies the exact five role IDs from the active predecessor so its audit snapshot is complete.
- Applicability is the half-open UTC-naive interval `[effective_from, effective_to)`; null
  `effective_to` is open-ended. The database enforces only a valid interval. Later services own
  current/effective resolution and any permitted publication-time relationship.
- The one non-null current identity is exactly `DG-GRANT-MANUAL-REVIEW|GLOBAL`. A current
  `REVOKED` row deliberately shadows all older active publications so resolution cannot fall back.
- Historical rows have null `current_identity_key`; publication payload fields remain immutable by
  contract. A later service may clear only the predecessor current key and advance its
  `updated_at` while atomically appending the exact successor.
- Role IDs are not required to differ. The customer requirement is separation of actual users at
  action time. One role may contain multiple distinct eligible users.
- The schema does not infer personnel membership from role names, permissions, a first matching
  user, seed data or environment configuration.
- A row, current key or role FK never grants permission, authorizes an operation, confirms official
  evidence or changes legal state.

## Frozen migration identity and precheck

| Item | Exact contract |
| --- | --- |
| migration file | `backend/alembic/versions/v8_grant_manual_review_role_carrier.py` |
| `revision` | `v8_grant_manual_review_role_01` |
| intended `down_revision` | `v8_future_annuity_exception_01` |
| branch / dependency labels | `None` / `None` |
| direction | forward-only; `downgrade()` raises `NotImplementedError("This is a forward-only migration")` |

This migration is serialized after the accepted future-annuity exception carrier. At contract
materialization time that predecessor is not yet the current repository head. Before RED or any
implementation edit, acquire `GLOBAL_ALEMBIC_HEAD` and re-run:

`cd backend && PYTHONPATH=. .venv/bin/alembic heads`

The exact required pre-implementation output is
`v8_future_annuity_exception_01 (head)`. If the future-annuity migration is absent/unaccepted, the
head differs, there is more than one head, or any frozen revision/table/class/constraint/index name
already exists, stop only this lane and re-freeze migration order. Do not guess another predecessor,
create a merge revision, absorb the competing schema task or silently skip a collision.

The migration uses SQLite-safe `op.create_table` followed by `op.create_index`. It performs no
alter, backfill, update, delete, role binding, permission change, seed, status coercion or data
publication. Correctness must not depend on `RETURNING` or a PostgreSQL-only type/function.

## Frozen ORM ownership

- ORM class: `GrantManualReviewRoleConfig`.
- ORM file: `backend/app/modules/system/models.py`.
- Table: `t_grant_manual_review_role_config`.
- Standard registry: `backend/app/models/__init__.py` imports and exports exactly
  `GrantManualReviewRoleConfig` in addition to its current names.
- Use explicit mapped columns, application UUIDs from `str(uuid4())`,
  `DateTime(timezone=False)` and explicit `CURRENT_TIMESTAMP` only for the two technical audit
  columns frozen below.
- Do not add a relationship, enum module, mixin, second table, generic configuration abstraction or
  compatibility column to an existing table.
- ORM metadata and migration must match exactly. No business field has a server default.

## Physical schema — `t_grant_manual_review_role_config`

The table has exactly these 21 columns and no others:

| Column | SQLAlchemy / ORM type | Nullable | Server default | Exact meaning |
| --- | --- | --- | --- | --- |
| `id` | `String(36)` / `Mapped[str]` | no | none | application UUID primary key |
| `gate_code` | `String(32)` / `Mapped[str]` | no | none | exact `DG-GRANT-MANUAL-REVIEW` |
| `scope_key` | `String(64)` / `Mapped[str]` | no | none | exact `GLOBAL` |
| `official_copy_acquirer_role_id` | `String(36)` / `Mapped[str]` | no | none | official-copy acquisition role |
| `first_verifier_role_id` | `String(36)` / `Mapped[str]` | no | none | first official-copy verification role |
| `second_verifier_role_id` | `String(36)` / `Mapped[str]` | no | none | second official-copy verification role |
| `manual_review_proposer_role_id` | `String(36)` / `Mapped[str]` | no | none | controlled manual-review proposal role |
| `manual_review_second_reviewer_role_id` | `String(36)` / `Mapped[str]` | no | none | manual-review second-review role |
| `config_version` | `String(128)` / `Mapped[str]` | no | none | globally unique immutable publication version |
| `config_status` | `String(32)` / `Mapped[str]` | no | none | `ACTIVE` or `REVOKED` |
| `effective_from` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | none | inclusive applicability start |
| `effective_to` | `DateTime(timezone=False)` / `Mapped[datetime \| None]` | yes | none | exclusive end; null is open-ended |
| `confirmed_by` | `String(36)` / `Mapped[str]` | no | none | authenticated institution configuration actor |
| `published_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | none | server-captured publication time |
| `supersedes_config_id` | `String(36)` / `Mapped[str \| None]` | yes | none | immediately prior current publication |
| `config_snapshot` | `Text` / `Mapped[str]` | no | none | immutable canonical JSON publication |
| `config_snapshot_hash` | `String(64)` / `Mapped[str]` | no | none | lowercase SHA-256 of exact snapshot bytes |
| `idempotency_key` | `String(128)` / `Mapped[str]` | no | none | immutable publication replay identity |
| `current_identity_key` | `String(128)` / `Mapped[str \| None]` | yes | none | exact current publication identity or null history |
| `created_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | insertion audit time |
| `updated_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | current-pointer transition audit time |

## Exact unique constraints and foreign keys

In addition to the primary key, create exactly these unique constraints:

- `uq_t_grant_manual_review_role_config_version` on `config_version`.
- `uq_t_grant_manual_review_role_config_idempotency_key` on `idempotency_key`.
- `uq_t_grant_manual_review_role_config_current_identity_key` on `current_identity_key`.
  SQLite permits multiple null historical values and at most one non-null current row.

Create exactly these foreign keys, all `ON DELETE RESTRICT`:

- `fk_t_grant_manual_role_config_acquirer_role`:
  `official_copy_acquirer_role_id -> t_role.id`.
- `fk_t_grant_manual_role_config_first_verifier_role`:
  `first_verifier_role_id -> t_role.id`.
- `fk_t_grant_manual_role_config_second_verifier_role`:
  `second_verifier_role_id -> t_role.id`.
- `fk_t_grant_manual_role_config_proposer_role`:
  `manual_review_proposer_role_id -> t_role.id`.
- `fk_t_grant_manual_role_config_second_reviewer_role`:
  `manual_review_second_reviewer_role_id -> t_role.id`.
- `fk_t_grant_manual_role_config_confirmed_by`: `confirmed_by -> t_user.id`.
- `fk_t_grant_manual_role_config_supersedes_config`:
  `supersedes_config_id -> t_grant_manual_review_role_config.id`.

The role FKs preserve the configured duty identities and prevent referenced roles from being
deleted. They intentionally do not target `t_user_role`: a configuration selects roles, while
actual personnel eligibility is dynamic and is revalidated by later services.

## Exact check constraints and index

Create exactly these named checks:

- `ck_t_grant_manual_review_role_config_gate`:
  `gate_code = 'DG-GRANT-MANUAL-REVIEW' AND scope_key = 'GLOBAL'`.
- `ck_t_grant_manual_review_role_config_status`:
  `config_status IN ('ACTIVE', 'REVOKED')`.
- `ck_t_grant_manual_review_role_config_interval`:
  `effective_to IS NULL OR effective_to > effective_from`.
- `ck_t_grant_manual_review_role_config_hash` requires exactly 64 lowercase hexadecimal
  characters:
  `length(config_snapshot_hash) = 64 AND config_snapshot_hash = lower(config_snapshot_hash) AND config_snapshot_hash NOT GLOB '*[^0-9a-f]*'`.
- `ck_t_grant_manual_review_role_config_current_key`:
  `current_identity_key IS NULL OR current_identity_key = gate_code || '|' || scope_key`.

Do not add a role-ID inequality check. The same configured role ID is valid in two slots when the
later action uses distinct eligible actual users.

Create exactly one non-unique index after the table exists:

- `ix_t_grant_manual_review_role_config_interval` on
  `(scope_key, config_status, effective_from, effective_to)`.

No role-column index, partial index, trigger, permission table or second current-pointer table is
added.

## Frozen canonical snapshot contract for later services

This task stores snapshot text/hash only and inserts no snapshot. A later service constructs UTF-8
canonical JSON using `ensure_ascii=False`, `sort_keys=True`, `separators=(",", ":")` and
`allow_nan=False`, then computes lowercase SHA-256 over the exact UTF-8 bytes.

Every `ACTIVE` or `REVOKED` snapshot has exactly these keys:

`schema`, `gate_code`, `scope_key`, `official_copy_acquirer_role_id`,
`first_verifier_role_id`, `second_verifier_role_id`, `manual_review_proposer_role_id`,
`manual_review_second_reviewer_role_id`, `config_version`, `config_status`, `effective_from`,
`effective_to`, `confirmed_by`, `published_at`, `expected_current_config_id`.

`schema` is exactly `FPMS_GRANT_MANUAL_REVIEW_ROLE_CONFIG_V1`; timestamps are UTC-naive ISO-8601
with microseconds and null remains JSON null. On revocation, the later service copies the five role
IDs from the exact active predecessor. Snapshot construction, hash recomputation, idempotency,
expected-current CAS and predecessor matching remain service behavior and are not implemented here.

## Database boundary versus later service/action invariants

This schema proves only structural completeness, role/user existence at insert time, immutable
publication identity format, current-row uniqueness and retained audit lineage. It cannot prove
live personnel eligibility or separation.

The later configuration service must, before publication and every resolution:

1. resolve the exact current source-backed Scheme A gate for
   `DG-GRANT-MANUAL-REVIEW:GLOBAL`;
2. validate canonical snapshot/hash, exact predecessor, idempotency and expected-current CAS;
3. require the current row to be unique, `ACTIVE` and effective at the caller-supplied instant;
4. require all five roles to exist and each to have at least one active `t_user` member through
   `t_user_role`;
5. require at least one pair of distinct active users across first/second verifier roles and at
   least one pair across proposer/second-reviewer roles;
6. return `409` with no write and no fallback for missing, future, expired, revoked, malformed,
   ambiguous or incomplete configuration/bindings.

Each later controlled action must additionally prove the authenticated actor is an active member of
the exact configured role at the action instant. The official-copy first and second actual user IDs
must differ; manual-review proposer and second-reviewer actual user IDs must differ. Existing
`GrantEvidenceCandidate` reinforces the latter pair only after those IDs are persisted. No role-ID
inequality may substitute for actual-user separation.

Operational evidence must later retain the exact role-configuration ID/hash used, actual actors,
official raw evidence, acquisition facts, reasons and action times. That behavior requires a
separate accepted schema/service task and is explicitly outside this carrier.

## Focused RED / GREEN schema-test contract

`backend/tests/test_v8_grant_manual_review_role_carrier_schema.py` must prove all and only the
following with explicit synthetic test-only users and roles:

1. RED fails on the absent ORM class/table/registry export/migration before implementation.
2. ORM metadata and reflected SQLite metadata expose the exact 21 columns in order, types,
   lengths, nullability and only the two frozen technical timestamp defaults.
3. The seven exact `RESTRICT` FKs, three unique constraints, five checks and one index have exact
   names, targets and column order in ORM and migration metadata.
4. The standard fresh-interpreter bootstrap `from app.models import *` resolves every FK target and
   exports `GrantManualReviewRoleConfig` exactly once.
5. One valid synthetic `ACTIVE` publication inserts only after five referenced roles and one
   confirming user exist; application UUID generation works after `flush()` without `RETURNING`.
6. Missing/null role slots, missing role/user/predecessor FKs and deletion of any referenced role,
   confirming user or predecessor are rejected with SQLite foreign keys enabled.
7. Invalid gate/scope/status, inverted interval, wrong-length/uppercase/non-hex hash and malformed
   current key are rejected independently.
8. Duplicate config version, idempotency key and non-null current identity fail independently;
   multiple historical null current keys remain valid.
9. The same role ID may occupy paired slots. The schema test must prove this is accepted and must
   not invent a role-ID inequality constraint or a production role identity.
10. A synthetic revoked successor with copied role IDs may own the current identity while its
    historical active predecessor has a null current key; no older-row fallback is inferred or
    tested as success.
11. Migration revision/down-revision/forward-only downgrade are exact and Alembic has one head
    `v8_grant_manual_review_role_01` after implementation.
12. A clean isolated SQLite `upgrade head` creates the table with zero rows, changes no existing
    row, creates no role/user/user-role/permission/configuration row and reports the exact head.

The focused test does not call a configuration service, endpoint, ingestion/review service,
lifecycle writer, seed, production database or external source.

## Dependencies, ownership and serialization

- The exact Scheme A source/adoption and `DG-GRANT-MANUAL-REVIEW:GLOBAL` policy remain mandatory.
- The accepted grant-source carrier remains an independent prerequisite; this task does not alter
  its source/config/candidate tables.
- The future-annuity exception schema migration must be accepted first and must expose the sole
  head `v8_future_annuity_exception_01` at implementation preflight.
- `GLOBAL_ALEMBIC_HEAD`, `backend/app/modules/system/models.py`,
  `backend/app/models/__init__.py` and all SQLite-writing verification have exclusive serialized
  ownership for this task.
- This task may not overlap another migration, system-model, standard-registry or SQLite writer.
  Shared-file dirt, changed head or object-name collision blocks this lane; it does not authorize
  absorbing or rewriting the competing work.

## Exact allowed files

- `tasks/postdemo/v8/FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SCHEMA-20260810-01.md`
- `backend/alembic/versions/v8_grant_manual_review_role_carrier.py`
- `backend/app/modules/system/models.py`
- `backend/app/models/__init__.py`
- `backend/tests/test_v8_grant_manual_review_role_carrier_schema.py`

No artifact source, second task, service, API, schema, router, permission, role, user, seed,
manifest, catalog, coverage-ledger, domain/source contract or unrelated test/source path is in the
implementation allowlist. Generated review/command evidence under
`artifacts/FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SCHEMA-20260810-01/**` is evidence output, not an
additional product/source edit permission. Preserve and report the initial tracked/untracked dirty
baseline without absorbing it.

## Explicit non-closure

- No production role ID, role code, user ID, personnel assignment or institution identity.
- No new role, user, `t_user_role`, `t_role_perm`, permission code, seed, bootstrap row, default,
  fallback or environment mapping.
- No configuration publication/revocation/resolver service, authorization check, request/response
  schema, API, router, UI or readiness endpoint.
- No operational official-copy acquisition, first/second verification, manual-review proposal or
  second-review behavior and no actor/action audit record.
- No change to `GrantEvidenceCandidate`, document/evidence version, source record/configuration,
  decision gate, lifecycle/legal status, deadline, fee, draft, payment or receipt behavior.
- No broad refactor, second table, generic repository/config abstraction, manifest/catalog/ledger
  edit, broad suite, release check, commit or push.

## Remaining follow-up tasks

- `FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SERVICE-20260810-01` — canonical publication,
  revocation and fail-closed role/personnel resolver; current CAS and no fallback.
- `FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-API-20260810-01` — authenticated institution-
  configuration API using the existing configuration permission; no new permission or role.
- `FPMS-V8-GRANT-EVIDENCE-OFFICIAL-COPY-VERIFICATION-CARRIER-SCHEMA-20260810-01` — separate
  operational acquisition/first/second verification actors, reasons, configuration lineage and
  actual-user separation.
- `FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01` — dependency/interface re-freeze before
  implementation; it must not infer acquisition actor from proposer.
- `FPMS-V8-GRANT-EVIDENCE-REVIEW-SERVICE-20260712-01` and its API — dependency/interface re-freeze
  to consume exact role configuration and enforce proposer/second-reviewer membership and actual-
  user separation.

## Verification commands for the implementation task

Do not run these during contract materialization.

- Serialized preflight before RED:
  `cd backend && PYTHONPATH=. .venv/bin/alembic heads`
  — exact output must be `v8_future_annuity_exception_01 (head)`.
- Focused RED:
  `cd backend && .venv/bin/pytest -q tests/test_v8_grant_manual_review_role_carrier_schema.py`
  — preserve the expected missing-carrier failure before implementation.
- Focused GREEN:
  `cd backend && .venv/bin/pytest -q tests/test_v8_grant_manual_review_role_carrier_schema.py`.
- Scoped Ruff, only on task-owned implementation files:
  `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_grant_manual_review_role_carrier.py app/modules/system/models.py ../backend/app/models/__init__.py tests/test_v8_grant_manual_review_role_carrier_schema.py && .venv/bin/ruff format alembic/versions/v8_grant_manual_review_role_carrier.py app/modules/system/models.py ../backend/app/models/__init__.py tests/test_v8_grant_manual_review_role_carrier_schema.py && .venv/bin/ruff check alembic/versions/v8_grant_manual_review_role_carrier.py app/modules/system/models.py ../backend/app/models/__init__.py tests/test_v8_grant_manual_review_role_carrier_schema.py`.
- Unique head after implementation:
  `cd backend && PYTHONPATH=. .venv/bin/alembic heads`
  — exact output must be `v8_grant_manual_review_role_01 (head)`.
- Clean isolated SQLite migration under the serialized queue:
  `cd backend && tmp_dir="$(mktemp -d)" && DATABASE_URL="sqlite:///${tmp_dir}/grant-manual-review-role-carrier.db" PYTHONPATH=. .venv/bin/alembic upgrade head && DATABASE_URL="sqlite:///${tmp_dir}/grant-manual-review-role-carrier.db" PYTHONPATH=. .venv/bin/alembic current`
  — exact current revision must be `v8_grant_manual_review_role_01 (head)` and the new table count
  must be zero as asserted by the focused test.
- Exact allowlist whitespace/diff check:
  `git diff --check -- tasks/postdemo/v8/FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SCHEMA-20260810-01.md backend/alembic/versions/v8_grant_manual_review_role_carrier.py backend/app/modules/system/models.py backend/app/models/__init__.py backend/tests/test_v8_grant_manual_review_role_carrier_schema.py`.

Do not run repo-wide tests, broad frontend/backend build, broad Playwright, seed, production DB
upgrade, milestone/full/final verification or release checks for this task.

## Independent High review and evidence

Because this story is `PROTECTED`, the implementer cannot approve it. One independent High
reviewer must review the exact implementation commit/range and independently rerun the decisive
focused GREEN, scoped Ruff, unique-head and clean temporary SQLite upgrade/current checks.

The review must bind:

- exact task SHA-256 and implementation commit/range;
- baseline-subtracted five-path patch and patch SHA-256;
- the exact Scheme A source/version/hash above;
- exact 21-column ORM/migration parity, constraints, seven `RESTRICT` FKs and index;
- zero production rows, identities, defaults, seeds, permissions, services or legal-state effects;
- actual-user separation remaining an explicit later service/action-time invariant with no role-ID
  inequality;
- one final `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`.

Evidence belongs under
`artifacts/FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SCHEMA-20260810-01/**` and must preserve the
initial dirty baseline, RED, final GREEN, Ruff, head, clean-upgrade, diff/scope and independent
review logs. Historical receipts or review of different bytes do not establish current acceptance.

## Acceptance order and done definition

1. Independently review and adopt this exact task contract. Contract review does not implement or
   approve the schema.
2. Accept the future-annuity schema first, then acquire the migration/system-model/registry/SQLite
   owners and confirm its exact revision is the sole head.
3. Preserve focused RED; implement only the five allowlisted paths; run focused GREEN, scoped Ruff,
   unique-head, clean isolated SQLite and exact diff checks.
4. Obtain independent High zero-finding review of the exact commit/range and decisive reruns.
5. Only after this schema is accepted may the separate role service begin. APIs and operational
   evidence/review consumers remain separately owned and disabled.

Done means the exact RED is preserved; the minimum one-table migration/ORM/registry/test change
makes focused GREEN and exact ORM/reflected parity pass; all five required role FKs, publication
version/hash/actor/time/audit fields, constraints, index, zero rows, unique head and clean SQLite
upgrade are independently verified; no role IDs are required to differ; no default, seed,
production identity, service, API or operational behavior exists; and an independent High reviewer
approves the exact commit/range with zero findings.

This contract-materialization change edits only this task file and is reported
`READY_FOR_INDEPENDENT_REVIEW`, never schema PASS.
