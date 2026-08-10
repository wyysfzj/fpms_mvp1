# FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01

Status: FROZEN CANDIDATE / READY FOR INDEPENDENT HIGH REVIEW
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates / grant-source prerequisite`
Executor role: Backend Developer / worker
Repository risk: HIGH

## Design References

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/execution.md`
- `docs/agents/evidence.md`
- `docs/agents/domain-safety.md`
- `docs/agents/source-authority.md`
- `docs/product/v8/source-decision-registry.md`
- `docs/postdemo/postdemo_v8_full_batch_decision_clarification_20260810.md`
- `docs/product/v8/reviews/V8-FULL-BATCH-CUSTOMER-DECISION-CURRENT-ADOPTION.md`
- `docs/product/v8/reviews/V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-CURRENT-ADOPTION.md`
- `tasks/batches/FPMS-POSTDEMO-V8-GRANT-SOURCE-GATE-20260712-01.md`
- Blocked consumer: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01.md`
- Customer gate requirement: `DG-GRANT-EVIDENCE-SOURCE[GLOBAL]`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SCHEMA`

- RED expectation: the focused schema test fails because the three named ORM carriers,
  tables, constraints or frozen migration are absent.
- GREEN expectation: exact ORM/reflected-SQLite parity, constraint behavior, one Alembic
  head and a clean isolated SQLite `upgrade head` pass without inserting any source,
  configuration, candidate or role row.

## Why this prerequisite is mandatory

The accepted customer decision is a configuration policy, not a concrete source. Existing
`t_customer_decision_gate` records only whether that policy is confirmed; it cannot represent a
reviewed and activated CNIPA directory entry or the institution administrator's selected source
version. Existing `t_document_evidence_version` retains the evidence file/version and review tuple
but has no immutable acquisition/source/configuration/reason/conflict carrier. Mutable
`Document.extra_data` is not an acceptable substitute for original evidence lineage.

Therefore the minimum fail-closed schema is exactly three records:

1. an independently reviewed and activated CNIPA source-directory version;
2. an append-only, versioned `GLOBAL` selection for one grant-evidence scope; and
3. an immutable candidate-provenance record binding the selected source/configuration to the
   existing evidence version and later second-person review.

Removing the third record leaves the already-frozen ingestion/read/review tasks unable to preserve
their required source/version/proposer/reviewer/reason/conflict data. Combining the directory and
selection records would allow an administrator to select a record that had never independently
passed the directory review boundary. Neither weakening is authorized.

## Frozen source and legal-state boundary

- `source_authority` is exactly `CNIPA`. This task does not choose a URL, API, query channel,
  dataset, file, version, acquisition method, effective date or production row.
- The only evidence scopes are `GRANT_ANNOUNCEMENT` and `PATENT_REGISTER`. They are independent:
  a valid configuration for one does not activate or unblock the other.
- The decision-gate scope remains exactly `GLOBAL`; no customer, case, department or role fallback
  is introduced.
- A directory record is usable only after a later service proves it is independently reviewed,
  activated and effective. A configuration is usable only after a later service proves its linked
  directory record is still usable for the same evidence scope and instant.
- Missing, future, expired, revoked, rejected, unreviewed, inactive, scope-mismatched,
  version/hash-mismatched or ambiguous data remains `409 / NO WRITE / NO LEGAL-STATE CHANGE` in
  later services. This schema creates no permissive fallback.
- `stale` is not an invented TTL. It means a persisted effective interval no longer covers the
  requested instant, a persisted current/status tuple is no longer usable, or an immutable
  version/hash/link no longer matches.
- Candidate presence, ingestion, review state or source activation never proves grant, never
  changes `Case.status`, and never emits a lifecycle event.

## Frozen migration identity and precheck

| Item | Exact contract |
| --- | --- |
| migration file | `backend/alembic/versions/v8_grant_evidence_source_carrier.py` |
| `revision` | `v8_grant_source_carrier_01` |
| `down_revision` | `v8_d31_overlay_conflict_01` |
| branch / dependency labels | `None` / `None` |
| direction | forward-only; `downgrade()` raises `NotImplementedError("This is a forward-only migration")` |

The contract-freeze precheck observed exactly one Alembic head,
`v8_d31_overlay_conflict_01`. Before implementation, the worker must re-run
`cd backend && PYTHONPATH=. .venv/bin/alembic heads`. If the result is not exactly that one head,
or any frozen table/class/constraint/index name already exists, stop this lane and return the task
for migration-order re-freeze. Do not guess a new `down_revision`, merge heads or silently skip a
collision.

The migration creates the tables in this order:

1. `t_grant_evidence_source_record`;
2. `t_grant_evidence_source_config`;
3. `t_grant_evidence_candidate`;
4. the exact named indexes after their columns and tables exist.

It uses SQLite-safe `op.create_table` / `op.create_index` operations only. It performs no alter,
backfill, data update, delete, source activation, role binding, seed or status coercion.

## Frozen ORM ownership

- `GrantEvidenceSourceRecord` and `GrantEvidenceSourceConfig` live in
  `backend/app/modules/system/models.py`.
- `GrantEvidenceCandidate` lives in `backend/app/modules/documents/models.py`.
- All three use explicit mapped columns, application UUIDs from `str(uuid4())`,
  `DateTime(timezone=False)` and explicit `CURRENT_TIMESTAMP` audit defaults. Do not add a
  relationship property, new enum module, repository abstraction or mixin.
- The ORM metadata and migration must match exactly. Correctness must not depend on SQLite
  `RETURNING`.

## Table 1 — `t_grant_evidence_source_record`

ORM class: `GrantEvidenceSourceRecord`. It has exactly these 26 columns and no others:

| Column | SQLAlchemy / ORM type | Nullable | Server default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `String(36)` / `Mapped[str]` | no | none | application UUID primary key |
| `source_authority` | `String(32)` / `Mapped[str]` | no | none | exactly `CNIPA` |
| `source_code` | `String(64)` / `Mapped[str]` | no | none | stable code within the authority-and-evidence-scope series; no value is seeded here |
| `source_version` | `String(128)` / `Mapped[str]` | no | none | immutable source version within the series |
| `evidence_scope` | `String(32)` / `Mapped[str]` | no | none | `GRANT_ANNOUNCEMENT` or `PATENT_REGISTER` |
| `source_reference_kind` | `String(32)` / `Mapped[str]` | no | none | exactly `DATA`, `QUERY_CHANNEL` or `FILE` |
| `source_reference_value` | `String(512)` / `Mapped[str]` | no | none | exact official data, query-channel or file reference selected by the kind |
| `acquisition_method` | `String(64)` / `Mapped[str]` | no | none | exact acquisition method; no default |
| `effective_from` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | none | inclusive applicability start |
| `effective_to` | `DateTime(timezone=False)` / `Mapped[datetime \| None]` | yes | none | exclusive applicability end; `NULL` is open-ended |
| `source_snapshot` | `Text` / `Mapped[str]` | no | none | immutable canonical JSON source record |
| `source_snapshot_hash` | `String(64)` / `Mapped[str]` | no | none | lowercase SHA-256 hex of exact snapshot text |
| `review_status` | `String(32)` / `Mapped[str]` | no | `'PENDING'` | `PENDING`, `APPROVED` or `REJECTED` |
| `reviewed_by` | `String(36)` / `Mapped[str \| None]` | yes | none | independent actual-user reviewer |
| `reviewed_at` | `DateTime(timezone=False)` / `Mapped[datetime \| None]` | yes | none | terminal review time |
| `review_reason` | `Text` / `Mapped[str \| None]` | yes | none | retained terminal review reason |
| `activation_status` | `String(32)` / `Mapped[str]` | no | `'INACTIVE'` | `INACTIVE`, `ACTIVE` or `RETIRED` |
| `activated_by` | `String(36)` / `Mapped[str \| None]` | yes | none | actor who first activates the reviewed version |
| `activated_at` | `DateTime(timezone=False)` / `Mapped[datetime \| None]` | yes | none | first activation time, retained after retirement |
| `supersedes_source_id` | `String(36)` / `Mapped[str \| None]` | yes | none | prior version with the same authority, evidence scope and source code |
| `current_identity_key` | `String(128)` / `Mapped[str \| None]` | yes | none | exact active identity `CNIPA\|<evidence_scope>\|<source_code>` |
| `idempotency_key` | `String(128)` / `Mapped[str]` | no | none | immutable registration replay identity |
| `created_by` | `String(36)` / `Mapped[str]` | no | none | proposing actual user |
| `created_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | creation audit time |
| `updated_by` | `String(36)` / `Mapped[str]` | no | none | last state-transition actor |
| `updated_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | last state-transition time |

### Source-record identities, constraints and index

- `uq_t_grant_evidence_source_record_series_version` is
  `UNIQUE(source_authority, evidence_scope, source_code, source_version)`.
- `uq_t_grant_evidence_source_record_idempotency_key` is `UNIQUE(idempotency_key)`.
- `uq_t_grant_evidence_source_record_current_identity_key` is
  `UNIQUE(current_identity_key)`; multiple `NULL` historical/inactive keys are valid on SQLite.
- `fk_t_grant_evidence_source_record_created_by`, `_updated_by`, `_reviewed_by` and
  `_activated_by` target `t_user.id`, `ON DELETE RESTRICT`; reviewer/activator FKs are nullable.
- `fk_t_grant_evidence_source_record_supersedes_source_id` targets this table's `id`,
  `ON DELETE RESTRICT`.
- `ck_t_grant_evidence_source_record_authority` requires
  `source_authority = 'CNIPA'`.
- `ck_t_grant_evidence_source_record_scope` restricts `evidence_scope` to the two frozen values.
- `ck_t_grant_evidence_source_record_reference_kind` restricts `source_reference_kind` to
  `DATA/QUERY_CHANNEL/FILE`; `source_reference_value` carries exactly the one selected official
  reference, so a source row does not require both a channel and a data/file name.
- `ck_t_grant_evidence_source_record_hash_length` requires
  `length(source_snapshot_hash) = 64`. Lowercase-hex and canonical-content validation belongs to
  the follow-up service.
- `ck_t_grant_evidence_source_record_interval` requires
  `effective_to IS NULL OR effective_to > effective_from`.
- `ck_t_grant_evidence_source_record_review_status` restricts status to
  `PENDING/APPROVED/REJECTED`.
- `ck_t_grant_evidence_source_record_review_tuple` requires `PENDING` to have null
  reviewer/time/reason, and terminal states to have non-null reviewer/time/reason with
  `reviewed_by <> created_by`. This is the independently reviewed source boundary.
- `ck_t_grant_evidence_source_record_activation_status` restricts status to
  `INACTIVE/ACTIVE/RETIRED`.
- `ck_t_grant_evidence_source_record_activation_tuple` requires:
  - `INACTIVE`: null activator/time/current key; a rejected source can only be inactive;
  - `ACTIVE`: approved review, non-null activator/time and exact current key
    `source_authority || '|' || evidence_scope || '|' || source_code`;
  - `RETIRED`: approved review, retained activator/time and null current key.
- `ix_t_grant_evidence_source_record_scope_interval` is non-unique on
  `(evidence_scope, activation_status, effective_from, effective_to)`.

No additional separation is invented between `reviewed_by` and `activated_by`; they may be the
same actual user. Only the approved requirement `reviewed_by <> created_by` is frozen here.
The follow-up source service must verify that a non-null `supersedes_source_id` has the same
`(source_authority, evidence_scope, source_code)` series identity; this cross-row equality is not
weakened into a SQLite trigger.

`source_snapshot` is UTF-8 canonical JSON serialized with `ensure_ascii=False`,
`sort_keys=True`, `separators=(",", ":")`, `allow_nan=False`. Its later service contract has
exact top-level keys `schema_version`, `source_authority`, `source_code`, `source_version`,
`evidence_scope`, `source_reference_kind`, `source_reference_value`, `acquisition_method`,
`effective_from` and `effective_to`; `schema_version` is exactly
`CNIPA_GRANT_EVIDENCE_SOURCE_V1`. This task stores text/hash only and inserts no snapshot.

## Table 2 — `t_grant_evidence_source_config`

ORM class: `GrantEvidenceSourceConfig`. It has exactly these 19 columns and no others:

| Column | SQLAlchemy / ORM type | Nullable | Server default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `String(36)` / `Mapped[str]` | no | none | application UUID primary key |
| `gate_code` | `String(32)` / `Mapped[str]` | no | none | exactly `DG-GRANT-EVIDENCE-SOURCE` |
| `scope_key` | `String(64)` / `Mapped[str]` | no | none | exactly `GLOBAL` |
| `evidence_scope` | `String(32)` / `Mapped[str]` | no | none | one frozen evidence scope |
| `source_record_id` | `String(36)` / `Mapped[str]` | no | none | selected directory version |
| `config_version` | `String(128)` / `Mapped[str]` | no | none | immutable publication version |
| `config_status` | `String(32)` / `Mapped[str]` | no | none | `ACTIVE` or `REVOKED` |
| `effective_from` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | none | inclusive selection start |
| `effective_to` | `DateTime(timezone=False)` / `Mapped[datetime \| None]` | yes | none | exclusive end; `NULL` is open-ended |
| `selected_by` | `String(36)` / `Mapped[str]` | no | none | authenticated institution-configuration actor |
| `published_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | none | publication audit time |
| `selection_reason` | `Text` / `Mapped[str]` | no | none | retained selection/revocation reason |
| `supersedes_config_id` | `String(36)` / `Mapped[str \| None]` | yes | none | immediately prior publication for the same identity |
| `config_snapshot` | `Text` / `Mapped[str]` | no | none | immutable canonical JSON publication request |
| `config_snapshot_hash` | `String(64)` / `Mapped[str]` | no | none | lowercase SHA-256 hex of exact config snapshot |
| `idempotency_key` | `String(128)` / `Mapped[str]` | no | none | immutable publication replay identity |
| `current_identity_key` | `String(160)` / `Mapped[str \| None]` | yes | none | exact current publication identity |
| `created_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | row creation audit time |
| `updated_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | current-pointer transition audit time |

The exact non-null current key is
`DG-GRANT-EVIDENCE-SOURCE|GLOBAL|<evidence_scope>` for both `ACTIVE` and `REVOKED` current
publications. A revoked current row is retained so resolution cannot fall back to an older active
row.

### Configuration identities, constraints and index

- `uq_t_grant_evidence_source_config_version` is
  `UNIQUE(gate_code, scope_key, evidence_scope, config_version)`.
- `uq_t_grant_evidence_source_config_idempotency_key` is `UNIQUE(idempotency_key)`.
- `uq_t_grant_evidence_source_config_current_identity_key` is
  `UNIQUE(current_identity_key)`.
- `fk_t_grant_evidence_source_config_source_record_id` targets
  `t_grant_evidence_source_record.id`, `ON DELETE RESTRICT`.
- `fk_t_grant_evidence_source_config_selected_by` targets `t_user.id`,
  `ON DELETE RESTRICT`.
- `fk_t_grant_evidence_source_config_supersedes_config_id` targets this table's `id`,
  `ON DELETE RESTRICT`.
- `ck_t_grant_evidence_source_config_gate` requires the exact gate and `GLOBAL` scope.
- `ck_t_grant_evidence_source_config_scope` restricts `evidence_scope` to the two frozen values.
- `ck_t_grant_evidence_source_config_status` restricts status to `ACTIVE/REVOKED`.
- `ck_t_grant_evidence_source_config_interval` requires
  `effective_to IS NULL OR effective_to > effective_from`.
- `ck_t_grant_evidence_source_config_hash_length` requires
  `length(config_snapshot_hash) = 64`.
- `ck_t_grant_evidence_source_config_current_key` permits `NULL` for historical rows; every
  non-null value must equal the exact concatenated current key above. The follow-up service may
  clear a key only while atomically installing its explicit successor.
- `ix_t_grant_evidence_source_config_scope_interval` is non-unique on
  `(scope_key, evidence_scope, config_status, effective_from, effective_to)`.

The database cannot prove that the linked source is approved, active, effective, same-scope or
hash/version-identical to the publication snapshot. The follow-up source service must prove all of
those facts atomically before publication and again before every ingestion. It must use
idempotency plus expected-current CAS; this carrier does not invent a default configuration.

`config_snapshot` uses the same canonical JSON rules. Its later service contract has exact
top-level keys `schema_version`, `gate_code`, `scope_key`, `evidence_scope`, `source_record_id`,
`source_version`, `source_snapshot_hash`, `config_version`, `config_status`, `effective_from`,
`effective_to`, `selected_by`, `published_at`, `selection_reason` and
`expected_current_config_id`; `schema_version` is exactly
`CNIPA_GRANT_EVIDENCE_CONFIG_V1`.

## Table 3 — `t_grant_evidence_candidate`

ORM class: `GrantEvidenceCandidate`. It has exactly these 24 columns and no others:

| Column | SQLAlchemy / ORM type | Nullable | Server default | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `String(36)` / `Mapped[str]` | no | none | application UUID primary key |
| `case_id` | `String(36)` / `Mapped[str]` | no | none | owning case |
| `document_id` | `String(36)` / `Mapped[str]` | no | none | owning document |
| `evidence_version_id` | `String(36)` / `Mapped[str]` | no | none | immutable archived raw evidence version |
| `source_config_id` | `String(36)` / `Mapped[str]` | no | none | exact selected configuration used at acquisition |
| `source_record_id` | `String(36)` / `Mapped[str]` | no | none | exact directory version used at acquisition |
| `evidence_scope` | `String(32)` / `Mapped[str]` | no | none | one frozen evidence scope |
| `source_version_snapshot` | `String(128)` / `Mapped[str]` | no | none | copied immutable source version |
| `original_reference` | `String(512)` / `Mapped[str]` | no | none | exact official item/query/file reference |
| `acquisition_method_snapshot` | `String(64)` / `Mapped[str]` | no | none | exact acquisition method used |
| `acquired_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | none | acquisition instant |
| `acquisition_snapshot` | `Text` / `Mapped[str]` | no | none | canonical original acquisition/operator/reason record |
| `acquisition_snapshot_hash` | `String(64)` / `Mapped[str]` | no | none | lowercase SHA-256 hex of exact acquisition snapshot |
| `candidate_snapshot` | `Text` / `Mapped[str]` | no | none | canonical extracted facts, including conflicts without resolution |
| `candidate_snapshot_hash` | `String(64)` / `Mapped[str]` | no | none | lowercase SHA-256 hex of exact candidate snapshot |
| `proposed_by` | `String(36)` / `Mapped[str]` | no | none | proposing actual user; automated/process identity is not permitted |
| `proposed_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | none | proposal time |
| `review_status` | `String(32)` / `Mapped[str]` | no | `'PENDING'` | `PENDING`, `APPROVED` or `REJECTED` |
| `reviewer_id` | `String(36)` / `Mapped[str \| None]` | yes | none | second actual-user reviewer |
| `reviewed_at` | `DateTime(timezone=False)` / `Mapped[datetime \| None]` | yes | none | terminal review time |
| `review_reason` | `Text` / `Mapped[str \| None]` | yes | none | retained approval/rejection reason |
| `conflict_snapshot` | `Text` / `Mapped[str \| None]` | yes | none | canonical conflicting announcement/register facts; never silently selected |
| `created_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | candidate creation time |
| `updated_at` | `DateTime(timezone=False)` / `Mapped[datetime]` | no | `CURRENT_TIMESTAMP` | one terminal review transition time |

### Candidate identities, constraints and indexes

- `uq_t_grant_evidence_candidate_evidence_version_id` is `UNIQUE(evidence_version_id)`.
- `fk_t_grant_evidence_candidate_case_id` targets `t_case.id`, `ON DELETE RESTRICT`.
- `fk_t_grant_evidence_candidate_document_id` targets `t_document.id`, `ON DELETE RESTRICT`.
- `fk_t_grant_evidence_candidate_evidence_version_id` targets
  `t_document_evidence_version.id`, `ON DELETE RESTRICT`.
- `fk_t_grant_evidence_candidate_source_config_id` and `_source_record_id` target their exact
  carrier tables, `ON DELETE RESTRICT`.
- `fk_t_grant_evidence_candidate_proposed_by` and `_reviewer_id` target `t_user.id`,
  `ON DELETE RESTRICT`; reviewer is nullable.
- `ck_t_grant_evidence_candidate_scope` restricts `evidence_scope` to the two frozen values.
- `ck_t_grant_evidence_candidate_acquisition_hash_length` and
  `_candidate_hash_length` each require exact length 64.
- `ck_t_grant_evidence_candidate_review_status` restricts status to
  `PENDING/APPROVED/REJECTED`.
- `ck_t_grant_evidence_candidate_review_tuple` requires `PENDING` to have null
  reviewer/time/reason, and terminal states to have non-null reviewer/time/reason with
  `reviewer_id <> proposed_by`. This is the approved proposer/second-reviewer separation.
- `ix_t_grant_evidence_candidate_document_review` is non-unique on
  `(document_id, review_status, proposed_at)`.

The follow-up ingestion service must prove the case/document/evidence-version linkage, that the
configuration links the same directory row and scope, that the snapshots/hashes match, and that
`proposed_by` is the authenticated actual user. It must not substitute a process, synthetic or
default actor. Those cross-row facts are not weakened into SQLite triggers or denormalized defaults
here. A candidate row is append-once except for its single `PENDING -> APPROVED|REJECTED` review
tuple; no reopen, delete, legal-state field or direct lifecycle link is part of this carrier.

## Frozen RED / GREEN schema-test contract

`backend/tests/test_v8_grant_evidence_source_carrier_schema.py` must prove all of the following
without inserting a real source or role default:

1. RED fails because one or more frozen ORM classes/tables/migration are absent.
2. ORM metadata and clean reflected SQLite metadata expose exactly the frozen columns, types,
   lengths, nullability, defaults, constraints, FKs/delete actions and indexes.
3. Migration identity is exact and Alembic has one head: `v8_grant_source_carrier_01`.
4. Application UUIDs appear after `flush()` without `RETURNING`; synthetic rows are explicitly
   marked test-only and make no official-source claim.
5. Source authority/scope/reference-kind/hash/interval/status/tuple constraints reject invalid
   rows; each of `DATA`, `QUERY_CHANNEL` and `FILE` succeeds with its one selected reference;
   pending source rows allow no reviewer, approved/rejected rows require the full review tuple,
   and `reviewed_by == created_by` fails.
6. Source series/version and non-null current identities include `evidence_scope`: duplicate
   versions fail within one scope, the same code/version succeeds across the two scopes, and only
   one active current key succeeds per scope. Idempotency remains globally unique, multiple null
   historical keys succeed, and missing actor/supersedes FKs fail with SQLite foreign keys enabled.
7. Configuration gate/scope/status/hash/interval/current-key constraints and all three unique
   identities behave exactly; a missing source/actor/prior-config FK fails.
8. Candidate scope/hash/review-tuple constraints behave exactly; pending rows allow no reviewer,
   terminal rows require reason/actor/time, and `reviewer_id == proposed_by` fails.
9. Duplicate evidence-version candidates and missing case/document/evidence/source/config/user FKs
   fail; `proposed_by` must reference an existing `t_user`, no process/default proposer is seeded,
   and one consistent synthetic linkage succeeds.
10. Deleting a referenced case/document/evidence version/source/config/proposer/reviewer is
    restricted so no candidate audit lineage is erased; no legal-state row or lifecycle event is
    created.
11. A clean isolated SQLite `upgrade head` creates zero rows in all three new tables and preserves
    all pre-existing table data unchanged.

## Exact Closure Slice

Add only the exact three-table ORM/migration carrier required to represent an independently
reviewed and activated CNIPA source-directory version, one append-only global source selection per
grant-evidence scope, and immutable candidate acquisition/review provenance linked to the existing
document evidence version.

## Explicit Non-Closure

No source registration/review/activation/configuration/resolution service; no endpoint, request or
response schema; no source listing or review UI; no ingestion/read/review behavior; no lifecycle
dispatch or legal-state write; no seed/backfill/concrete CNIPA source; no role/permission/default
actor; no `DG-GRANT-MANUAL-REVIEW` role-binding carrier; no arbitrary freshness TTL; no manifest,
catalog, coverage ledger, customer-source or release change. Do not absorb another V8 row or
reinterpret Scheme A.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-CONTRACTS-20260712-01`
- `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- `FPMS-V8-DECISION-GATE-CARRIER-20260712-01`
- `FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01`

### External, gate and inherited prerequisites

- Accepted Scheme A customer-decision/current-owner adoption.
- Accepted grant-source lane activation remains policy-only; this prerequisite does not publish a
  runtime source.
- `GLOBAL_ALEMBIC_HEAD` lock.

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD`: exclusive owner for the complete task; no concurrent migration task.
- `backend/app/modules/system/models.py`: exclusive task owner while this task is active.
- `backend/app/modules/documents/models.py`: exclusive task owner while this task is active.
- All schema tests and SQLite writes run through the global serialized queue.

## Remaining Follow-Up Task IDs

- `FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01` — canonical snapshot/hash
  validation; source register, independent review/activation, configuration publish/revoke,
  idempotency/CAS and exact `(evidence_scope, as_of)` fail-closed resolver; caller-owned
  transaction; no concrete source.
- `FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01` — authenticated institution
  configuration endpoints using an existing permission injection, actor from the authenticated
  user, no role/default/seed/UI.
- `FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SCHEMA-20260810-01` — separate
  `DG-GRANT-MANUAL-REVIEW` role-binding carrier and its independent actual-user separation; it must
  not be inferred by this task.
- `FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01` — re-freeze its dependency/allowlist so
  it consumes the accepted resolver and candidate carrier before implementation.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01.md`
- `backend/alembic/versions/v8_grant_evidence_source_carrier.py`
- `backend/app/modules/system/models.py`
- `backend/app/modules/documents/models.py`
- `backend/tests/test_v8_grant_evidence_source_carrier_schema.py`
- `artifacts/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01/**`

No other source, test, task, manifest or shared-ownership file is authorized. Inherited regression
inputs are read-only. Preserve the captured dirty baseline; baseline-subtracted scope must contain
only this task's allowlisted paths.

## Runtime Contracts

- This schema task has no runtime activation and no service-level transaction.
- A later source resolver must complete before any `Document`, `DocAttachment`,
  `DocumentEvidenceVersion` or `GrantEvidenceCandidate` write begins.
- Missing or invalid source state stays `409 / NO WRITE / NO LEGAL-STATE CHANGE`; database rows do
  not themselves confer authority.
- No service or API may use `Document.extra_data`, an unreviewed `CustomerDecisionGate` value, a
  seed, environment variable or role name as a source fallback.
- Preserve SQLite foreign-key behavior: candidate provenance restricts deletion of its referenced
  case, document, evidence version, source, config and users; no cascade may erase candidate audit.

## Verification Commands

- Preflight before RED: `cd backend && PYTHONPATH=. .venv/bin/alembic heads  # exact output before implementation: v8_d31_overlay_conflict_01 (head)`.
- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_source_carrier_schema.py`; run before implementation and preserve the expected missing-carrier failure.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_source_carrier_schema.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_grant_evidence_source_carrier.py app/modules/system/models.py app/modules/documents/models.py tests/test_v8_grant_evidence_source_carrier_schema.py && .venv/bin/ruff format alembic/versions/v8_grant_evidence_source_carrier.py app/modules/system/models.py app/modules/documents/models.py tests/test_v8_grant_evidence_source_carrier_schema.py && .venv/bin/ruff check alembic/versions/v8_grant_evidence_source_carrier.py app/modules/system/models.py app/modules/documents/models.py tests/test_v8_grant_evidence_source_carrier_schema.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads  # exact output after implementation: v8_grant_source_carrier_01 (head)`
- `cd backend && tmp_dir="$(mktemp -d)" && DATABASE_URL="sqlite:///${tmp_dir}/grant-evidence-source-carrier.db" PYTHONPATH=. .venv/bin/alembic upgrade head && DATABASE_URL="sqlite:///${tmp_dir}/grant-evidence-source-carrier.db" PYTHONPATH=. .venv/bin/alembic current  # exact current: v8_grant_source_carrier_01 (head)`
- `git diff --check -- backend/alembic/versions/v8_grant_evidence_source_carrier.py backend/app/modules/system/models.py backend/app/modules/documents/models.py backend/tests/test_v8_grant_evidence_source_carrier_schema.py tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01.md`
- `./scripts/task_validate.sh FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, migration-head and
  clean-upgrade logs, and dirty-baseline artifacts when applicable.

## Acceptance and adoption order

1. This exact task-contract file receives independent HIGH zero-finding review and explicit
   governance adoption; contract review does not implement or approve the schema.
2. The active grant-source manifest is explicitly revised/adopted to insert this schema task, then
   the source service and API follow-ups, before the blocked ingestion task. A previous terminal
   manifest receipt cannot silently absorb changed governance bytes.
3. Execute this task under the global Alembic and two model-file locks. Preserve RED, implement the
   exact migration/ORM/test only, and obtain independent task acceptance.
4. Only after this task is accepted may the source service execute; only after that service is
   accepted may its API execute.
5. Only after accepted schema + service + API and explicit ingestion-task dependency re-freeze may
   grant-evidence ingestion start. The separate manual-review role carrier remains required before
   review/dispatch, and release remains last.

## Done Definition

The exact RED is preserved; the minimum allowlisted migration/ORM/test change makes the exact GREEN
and clean SQLite upgrade pass; unique-head, task-scoped lint/format/scope and dirty-baseline checks
pass; no row/default/source/role/legal-state side effect exists; an independent reviewer approves
the exact closure and non-closure; atomic evidence validation and
`./scripts/task_validate.sh FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01` pass. Only then
may the implementation task be reported PASS. This contract-materialization step alone is reported
`TASK_CONTRACT_READY`, never schema PASS.
