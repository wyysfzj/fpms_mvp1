# FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01

Status: FROZEN CANDIDATE / READY FOR INDEPENDENT HIGH REVIEW
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Backend Developer / worker
Repository risk: `HIGH`
Task Contract Profile: `TC-SERVICE`

## Authority and Design References

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/execution.md`
- `docs/agents/evidence.md`
- `docs/agents/domain-safety.md`
- `docs/agents/source-authority.md`
- `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`
- `docs/product/v8/source-decision-registry.md`, decision
  `DEC-V8-FULL-BATCH-SCHEME-A-20260810`
- `docs/product/v8/reviews/V8-FULL-BATCH-CUSTOMER-DECISION-CURRENT-ADOPTION.md`
- `docs/product/v8/reviews/V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-CURRENT-ADOPTION.md`
- `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01.md`
- Required schema adoption:
  `V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-CURRENT-ADOPTION`
- Required successor manifest activation:
  `FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01`

Frozen authority:

- Gate: `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`.
- Decision value: `APPROVED_POLICY`.
- Decision version: `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`.
- Decision source:
  `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`.
- Decision source SHA-256:
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.

The accepted policy permits an institution administrator to select, per grant-evidence scope,
only a reviewed and activated CNIPA source record. This service creates no source or configuration
by default. Missing, stale, future, expired, revoked, unreviewed, inactive, corrupt or ambiguous
authority is `409 / NO WRITE / NO LEGAL-STATE CHANGE`.

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

- RED expectation: the focused service test fails because the named service module and exact
  register/review/activate/retire/config/resolve behavior do not exist.
- GREEN expectation: the focused service test and the accepted decision-gate read regression pass
  with exact canonical bytes, replay, CAS, fail-closed resolution and caller-owned transactions.

## Activation Gate

Product work must not start until both of these are current and independently accepted:

1. `V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-CURRENT-ADOPTION` binds the accepted schema task,
   migration, ORM carriers, standard registry and focused schema evidence.
2. `FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01` is re-frozen to this exact task hash
   and the accepted schema/API/ingestion successor order, replaces the obsolete manifest ordering,
   prevents old and successor rows from both executing, and reaches terminal independent HIGH
   PASS.

A missing or stale adoption, changed schema bytes, manifest still naming the obsolete execution
order, or hash mismatch blocks only this lane. This task card does not activate product behavior.

## Exact Closure Slice

Add one synchronous system service that, against the accepted carrier schema:

1. registers an immutable CNIPA source version;
2. records one independent actual-user approval or rejection;
3. activates an approved source version or retires the current version with expected-current CAS;
4. appends and atomically installs one `GLOBAL` active or revoked configuration publication;
5. resolves exactly one current effective source/config pair for
   `(evidence_scope, as_of)` only after the exact source-backed decision gate resolves.

Registration, review, activation and config publication/revocation have the exact replay behavior
frozen below; explicit retirement is CAS-only and is never inferred as replay from an automatic
predecessor retirement. All writes are caller-transaction-owned. Resolution is read-only. No
candidate, document, evidence, lifecycle, role-binding or legal-state row is written.

## Frozen Module and Public Interface

Create exactly `backend/app/modules/system/grant_evidence_source_service.py`. It defines the exact
string enums `GrantEvidenceScope` (`GRANT_ANNOUNCEMENT`, `PATENT_REGISTER`),
`GrantEvidenceSourceReferenceKind` (`DATA`, `QUERY_CHANNEL`, `FILE`),
`GrantEvidenceSourceReviewDecision` (`APPROVED`, `REJECTED`) and
`GrantEvidenceSourceDisposition` (`CREATED`, `CHANGED`, `REUSED`). Raw strings and enum lookalikes
are not coerced.

The module exposes frozen, slotted, keyword-only command DTOs with these exact fields and order:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterGrantEvidenceSourceCommand:
    source_code: str
    source_version: str
    evidence_scope: GrantEvidenceScope
    source_reference_kind: GrantEvidenceSourceReferenceKind
    source_reference_value: str
    acquisition_method: str
    effective_from: datetime
    effective_to: datetime | None
    supersedes_source_id: str | None
    actor_id: str
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewGrantEvidenceSourceCommand:
    source_record_id: str
    decision: GrantEvidenceSourceReviewDecision
    reviewer_id: str
    reviewed_at: datetime
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ActivateGrantEvidenceSourceCommand:
    source_record_id: str
    actor_id: str
    activated_at: datetime
    expected_current_source_id: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class RetireGrantEvidenceSourceCommand:
    source_record_id: str
    actor_id: str
    retired_at: datetime
    expected_current_source_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishGrantEvidenceSourceConfigCommand:
    evidence_scope: GrantEvidenceScope
    source_record_id: str
    config_version: str
    effective_from: datetime
    effective_to: datetime | None
    selected_by: str
    published_at: datetime
    selection_reason: str
    expected_current_config_id: str | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RevokeGrantEvidenceSourceConfigCommand:
    evidence_scope: GrantEvidenceScope
    config_version: str
    effective_from: datetime
    selected_by: str
    published_at: datetime
    selection_reason: str
    expected_current_config_id: str
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolveGrantEvidenceSourceCommand:
    evidence_scope: GrantEvidenceScope
    as_of: datetime
```

`ActivateGrantEvidenceSourceCommand` has no second predecessor input. Its
`expected_current_source_id` is both the current-series CAS expectation and the value that must
exactly equal the target row's durable `supersedes_source_id`, including `None`.

It exposes these exact synchronous callables, with no service class, repository abstraction,
async wrapper, implicit session or clock read:

```python
def register_grant_evidence_source(
    command: RegisterGrantEvidenceSourceCommand, transaction: Session
) -> GrantEvidenceSourceRecordResult: ...

def review_grant_evidence_source(
    command: ReviewGrantEvidenceSourceCommand, transaction: Session
) -> GrantEvidenceSourceRecordResult: ...

def activate_grant_evidence_source(
    command: ActivateGrantEvidenceSourceCommand, transaction: Session
) -> GrantEvidenceSourceRecordResult: ...

def retire_grant_evidence_source(
    command: RetireGrantEvidenceSourceCommand, transaction: Session
) -> GrantEvidenceSourceRecordResult: ...

def publish_grant_evidence_source_config(
    command: PublishGrantEvidenceSourceConfigCommand, transaction: Session
) -> GrantEvidenceSourceConfigResult: ...

def revoke_grant_evidence_source_config(
    command: RevokeGrantEvidenceSourceConfigCommand, transaction: Session
) -> GrantEvidenceSourceConfigResult: ...

def resolve_grant_evidence_source(
    command: ResolveGrantEvidenceSourceCommand, transaction: Session
) -> GrantEvidenceSourceResolution: ...
```

The result DTOs are frozen, slotted and keyword-only with these exact fields, order and types:

```python
class GrantEvidenceSourceRecordResult:
    source_record_id: str
    review_status: str
    activation_status: str
    source_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantEvidenceSourceDisposition

class GrantEvidenceSourceConfigResult:
    config_id: str
    config_status: str
    config_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantEvidenceSourceDisposition

class GrantEvidenceSourceResolution:
    gate_id: str
    config_id: str
    config_snapshot_hash: str
    source_record_id: str
    evidence_scope: GrantEvidenceScope
    source_code: str
    source_version: str
    source_snapshot_hash: str
    source_reference_kind: GrantEvidenceSourceReferenceKind
    source_reference_value: str
    acquisition_method: str
    effective_from: datetime
    effective_to: datetime | None
```

No ORM row is returned.

## Validation and Error Boundary

- Exact runtime DTO/enum types, canonical UUID strings, nonblank bounded strings, naive datetimes,
  and interval shape are validated before any query. Invalid caller input is
  `GRANT_EVIDENCE_SOURCE_INPUT_INVALID` status `400` with `{"field": "<field>"}`.
- Timestamps are timezone-naive UTC. No value is trimmed, normalized, case-folded or defaulted.
- After input validation and before a connection, gate read, savepoint or business query, every
  public entrypoint rejects `transaction.new`, `transaction.dirty` or `transaction.deleted` as
  `GRANT_EVIDENCE_SOURCE_TRANSACTION_DIRTY` status `409`.
- Missing rows/users, stale expected-current values, idempotency mismatch, illegal transition,
  duplicate/malformed lineage, source/config scope mismatch, corrupt canonical bytes/hash,
  inactive/unreviewed/future/expired/revoked authority and ambiguity fail
  `GRANT_EVIDENCE_SOURCE_CONFLICT` status `409` with zero write.
- Accepted `resolve_decision_gate` errors retain their existing exact `409` code/details. The
  service does not translate them into success or fall back to another source/config row.

## Canonical Source Registration and Review

Registration always stores `source_authority="CNIPA"`, `review_status="PENDING"`,
`activation_status="INACTIVE"`, null review/activation/current fields, and the caller actor in
`created_by` and `updated_by`. A non-null `supersedes_source_id` must name a different source with
the exact same `(CNIPA, evidence_scope, source_code)` identity. The value is immutable activation
lineage, not advisory metadata. Registration never activates a source or changes its predecessor.

The service constructs `source_snapshot`; the caller never supplies snapshot text or hash. UTF-8
canonical JSON uses `ensure_ascii=False`, `sort_keys=True`, `separators=(",", ":")`, and
`allow_nan=False`. The exact keys are `schema_version`, `source_authority`, `source_code`,
`source_version`, `evidence_scope`, `source_reference_kind`, `source_reference_value`,
`acquisition_method`, `effective_from`, and `effective_to`. `schema_version` is
`CNIPA_GRANT_EVIDENCE_SOURCE_V1`; datetimes use naive UTC ISO-8601 with microseconds; null remains
JSON null. The stored hash is lowercase SHA-256 of the exact UTF-8 bytes.

An exact registration idempotency-key replay validates the immutable snapshot and binds the
requested `supersedes_source_id` against the row's durable field, returns `REUSED`, observes any
later review/activation state and performs no write. The same key with any different immutable
fact or predecessor value, including `None` versus non-null, is `409`.

Review is a single `PENDING -> APPROVED|REJECTED` compare-and-set. The reviewer must reference an
existing user and differ from `created_by`; reason is mandatory. Exact terminal replay with the
same decision/reviewer/time/reason returns `REUSED`; any changed repeat is `409`. Review does not
activate, retire, replace or configure a source.

## Source Activation and Retirement

Activation requires an exact approved, inactive, canonical-hash-valid source. Before any state
change, `command.expected_current_source_id` must exactly equal both the target's immutable
`supersedes_source_id` and the unique current source for the exact
`(CNIPA, evidence_scope, source_code)` series, including the all-`None` initial-series case. A
target registered against `None` cannot replace a current row, and a target registered against one
predecessor cannot activate over another. If the bound predecessor exists it must be approved,
active and canonical; within one savepoint it is changed to `RETIRED`, its current key is cleared
and its `updated_by/updated_at` are set to the new activation actor/time before the target becomes
`ACTIVE` with its exact current key. The target's `activated_by/activated_at` are set only on first
activation.

Activation replay is resolved before current actionability checks. It validates the command's
`expected_current_source_id` against the target's durable `supersedes_source_id` and validates the
stored activation actor/time and target lineage; an exact replay returns `REUSED` even if the
target was later explicitly retired, without reactivating or rewinding it. A changed predecessor,
actor, time or target is `409`.

Explicit retirement requires `expected_current_source_id == source_record_id`, exact current-key
ownership and an approved active target. It changes only activation status/current key and
`updated_by/updated_at`; it retains first activation actor/time. A predecessor retired inside a
successful activation is state-idempotent only for activation race recovery: observing that exact
predecessor already retired together with the exact activated successor may complete the same
activation as `REUSED` without another write. It is explicitly not replay evidence for
`RetireGrantEvidenceSourceCommand`. Because the schema has no durable explicit-retire operation
identity, an explicit retire command against any already-retired row returns `409`, even if its
actor/time happen to equal an automatic predecessor retirement; explicit retire returns `CHANGED`
only for its one successful CAS. Stale CAS or concurrent unique/CAS loss is `409` with zero partial
transition.

## GLOBAL Configuration Publication and Revocation

Before publish or revoke, the service calls existing `resolve_decision_gate` with
`DecisionGateCode.GRANT_EVIDENCE_SOURCE`, `scope_key="GLOBAL"`, and
`as_of=command.published_at`. It requires resolved scope `GLOBAL`, decision value
`APPROVED_POLICY`, and the exact frozen decision source/version above. The independently accepted
adoption binds the source SHA; runtime filesystem hashing or a second decision store is forbidden.

Publication requires an approved active canonical source in the same evidence scope. The source
interval must cover the complete config interval: source start is no later than config start, and
a bounded source end must be no earlier than a bounded config end; an open config is invalid for a
bounded source. `expected_current_config_id` must equal the unique current config for
`DG-GRANT-EVIDENCE-SOURCE|GLOBAL|<evidence_scope>`, including `None`.

Revocation requires an exact current `ACTIVE` config and matching expected ID. It copies that
config's source identity, stores `config_status="REVOKED"`, uses the command `effective_from` as
the revocation effect time and stores `effective_to=NULL`. A revoked row owns the current identity
so resolution never falls back to the superseded active publication.

Publish and revoke append a new row. In one savepoint they clear only the exact predecessor current
key, insert the successor with the same exact current key, and set `supersedes_config_id` to that
predecessor. They never update/delete a historical row otherwise.

The service constructs `config_snapshot` and hash. Its exact keys are `schema_version`,
`gate_code`, `scope_key`, `evidence_scope`, `source_record_id`, `source_version`,
`source_snapshot_hash`, `config_version`, `config_status`, `effective_from`, `effective_to`,
`selected_by`, `published_at`, `selection_reason`, and `expected_current_config_id`.
`schema_version` is `CNIPA_GRANT_EVIDENCE_CONFIG_V1`; gate/scope are exactly
`DG-GRANT-EVIDENCE-SOURCE`/`GLOBAL`; serialization and hashing use the same rules as source
registration. Exact idempotency replay returns the original row as `REUSED` even after a later
successor, performs no write and never rewinds the current pointer. Payload or lineage mismatch is
`409`.

## Fail-Closed Resolution

`resolve_grant_evidence_source` is read-only and performs no flush. It:

1. resolves the exact current source-backed decision gate for `GLOBAL` at caller `as_of` and
   validates its Scheme A value/source/version;
2. selects the one row whose current key is
   `DG-GRANT-EVIDENCE-SOURCE|GLOBAL|<evidence_scope>`; zero or multiple rows fail;
3. validates exact canonical config bytes/hash, `ACTIVE` status, scope and half-open applicability
   `effective_from <= as_of < effective_to` with null end open;
4. loads exactly the linked source and validates canonical source bytes/hash, CNIPA authority,
   approved review tuple, `ACTIVE` status/current key, same scope/version/hash as the config and
   the same half-open applicability at `as_of`;
5. returns immutable copied facts only after all validation succeeds.

Missing, future, expired, revoked, unreviewed, rejected, inactive, retired, scope/version/hash/
lineage mismatch, a non-current link, malformed snapshot, or ambiguity is `409`. A revoked/future/
corrupt current config or source shadows history; no older active row, environment value, seed,
role name, `Document.extra_data` or unreviewed gate value is used as fallback.

## Caller-Owned Transaction and Concurrency

- No function calls `commit()`, `rollback()`, `close()` or begins an independent session.
- Writes establish a real SQLite outer `BEGIN` when needed, then use one nested savepoint. A later
  caller rollback removes the complete mutation.
- Reads use `no_autoflush`; dirty caller state is rejected before it can flush.
- Expected-current compare-and-set predicates and database unique constraints are both mandatory.
  Integrity/CAS races are reconciled by exact replay or return `409`; no retry invents authority.
- Source/config state changes and SQLite-writing tests are globally serialized. Resolver tests may
  not overlap another SQLite writer.

## Frozen RED / GREEN Test Contract

`backend/tests/test_v8_grant_evidence_source_carrier_service.py` must prove all of the following
with synthetic, explicitly test-only source facts:

1. Exact enums, DTO fields/order/types, result fields and seven synchronous function signatures.
2. Registration canonical bytes/hash, no activation/default, same-series supersedes validation,
   durable predecessor binding, exact replay after later state, and changed-payload/predecessor
   idempotency conflict including `None` mismatch.
3. Independent review separation, approval/rejection shape, terminal replay and illegal transition.
4. Activation requires `target.supersedes_source_id == command.expected_current_source_id ==`
   the actual current series ID, including all-`None`; activation replay binds that durable field.
   Automatic predecessor retirement is state-idempotent only for the same activation/recovery and
   never counts as explicit-retire replay; repeated explicit retire of an already-retired row is
   `409`. Stale and serialized concurrent attempts leave one current source and no partial
   transition.
5. Publish/revoke require the exact current Scheme A gate, source approval/activation/scope/hash/
   interval coverage and expected-current config CAS; revoked current state blocks fallback.
6. Config canonical bytes/hash, predecessor chain, exact idempotent replay after later successors
   and changed-key/payload conflicts.
7. Successful resolution for each evidence scope returns the exact source/config lineage,
   including immutable `config_snapshot_hash` and `source_snapshot_hash`, and makes no write.
8. Missing/future/expired/revoked config; missing/rejected/unreviewed/inactive/retired/non-current
   source; scope/version/hash/snapshot/lineage mismatch; corrupt multiplicity; and gate
   absence/revocation/future/source/version mismatch all fail `409` with zero write.
9. Invalid DTO/enum/UUID/string/time/interval input is exact `400`; dirty session is exact `409`
   before connection/gate/query/savepoint/writer calls.
10. Forced faults and caller rollback remove the whole write; service never commits or rolls back;
    SQLite outer transaction and savepoint behavior are explicit.
11. No candidate/document/evidence/activity/legal-state/role/default/seed row is created or changed.

## Dependencies and Serialization

Required current accepted prerequisites:

- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`.
- `V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-CURRENT-ADOPTION`.
- terminal independent HIGH PASS of
  `FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01`, bound to this exact task hash and the
  accepted schema task/adoption.
- exact current persisted `DG-GRANT-EVIDENCE-SOURCE:GLOBAL` Scheme A decision at runtime.

`backend/app/modules/system/grant_evidence_source_service.py` and all focused SQLite verification
have one serialized owner. The existing
`backend/app/modules/system/decision_gate_service.py` is a read-only dependency and must not be
edited. A changed carrier schema, manifest, gate interface or concurrent SQLite writer is a stop
condition, not permission to absorb another file.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01.md`
- `backend/app/modules/system/grant_evidence_source_service.py`
- `backend/tests/test_v8_grant_evidence_source_carrier_service.py`
- `artifacts/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01/**`

No model, migration, registry, decision-gate service, API, router, schema, permission, role,
document, ingestion, lifecycle, seed, manifest, catalog, ledger or other test/source path is
authorized. Preserve and subtract the complete initial tracked/untracked dirty baseline.

## Explicit Non-Closure

- No API/UI/runtime router or permission wiring.
- No concrete CNIPA source, config, seed, bootstrap row, default, fallback or environment value.
- No `DG-GRANT-MANUAL-REVIEW` role binding or actor-role authorization; later API actors come from
  authenticated users under its separately frozen permission contract.
- No candidate ingestion/read/review, document/evidence write, lifecycle/legal-status conclusion,
  patent-in-force transition, deadline, fee, payment or external network acquisition.
- No schema/migration/model/registry change, repair path, destructive mutation, second service
  module, generic repository, adjacent refactor, broad suite, release gate, commit or push.

## Remaining Follow-Up Task IDs

- `FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01` — authenticated institution
  configuration endpoints using these exact service functions; no duplicated resolver logic.
- `FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SCHEMA-20260810-01` — separate actual-user role
  bindings and separation.
- `FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01` — dependency/allowlist re-freeze to
  consume only the accepted resolver and candidate carrier.

## Verification Commands

Initialize evidence only after both activation prerequisites are current and the serialized owner
receives the execution grant.

- RED: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_source_carrier_service.py`.
- GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_source_carrier_service.py`.
- Read-only inherited regression:
  `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_read_service.py`.
- Task-owned formatting followed by final check-only lint:
  `cd backend && .venv/bin/ruff check --fix app/modules/system/grant_evidence_source_service.py tests/test_v8_grant_evidence_source_carrier_service.py && .venv/bin/ruff format app/modules/system/grant_evidence_source_service.py tests/test_v8_grant_evidence_source_carrier_service.py && .venv/bin/ruff check app/modules/system/grant_evidence_source_service.py tests/test_v8_grant_evidence_source_carrier_service.py`.
- Scope/whitespace:
  `git diff --check -- tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01.md backend/app/modules/system/grant_evidence_source_service.py backend/tests/test_v8_grant_evidence_source_carrier_service.py`.
- Task gate, only after final independent HIGH zero-finding review:
  `./scripts/task_validate.sh FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01`.
- Atomic evidence, only after successful task gate:
  `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01 --required-step lint --required-step test --required-step independent_review --required-step scope --required-step task_gate`.

Do not run repo-wide tests, broad Playwright, production DB operations, seed, Foundation/Full/Final
close or release gate.

## Evidence Path

- `artifacts/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01/**`

Required PASS evidence includes `task.json`, `results.jsonl`, `summary.md`, `git/diff.patch`, all
command logs, complete dirty-baseline artifacts, preserved exact RED, final GREEN, inherited gate
regression, scoped lint/scope logs, caller-rollback and zero-side-effect counts, and serialized
SQLite execution. The independent HIGH review must bind the final baseline-subtracted patch hash
and current task/summary hashes with one `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`.
Latest `lint`, `test`, `scope`, `independent_review`, `task_gate` and `atomic_evidence` results must
all be successful.

## Acceptance and Adoption Order

1. Independently review and adopt this exact service contract; contract review does not implement
   or approve product code.
2. Accept the schema candidate and its current adoption, including standard registry resolution.
3. Re-freeze and independently accept the successor grant-source manifest activation to the exact
   schema/adoption/service task hashes and successor order.
4. Execute this task alone under the service/SQLite locks; preserve RED, implement only the exact
   service/test, run scoped checks and obtain independent HIGH acceptance.
5. Only after current service acceptance may the API task start. Ingestion remains blocked until
   schema + service + API acceptance and its own explicit dependency re-freeze. Release is last.

## Done Definition

The exact successor activation and schema current adoption are terminal/current; the exact RED is
preserved; the minimum two-file product/test implementation makes every frozen register/review/
activate/retire/publish/revoke/resolve case GREEN; canonical bytes/hash, idempotency, expected-current
CAS including durable source-predecessor binding, activation-only automatic-retirement recovery,
fail-closed gate/source/config resolution, dirty ordering, caller rollback, no-write failures and
SQLite serialization are evidenced; inherited decision-gate regression, scoped lint/scope,
independent HIGH review, task gate and atomic evidence all pass. No API/role/ingestion/legal-state
or concrete-source closure is absorbed. Only then may this implementation task report PASS.

This materialization turn edits only this task file and reports `TASK_CONTRACT_READY`, never
service PASS.
