# FPMS-V8-FUTURE-ANNUITY-EXCEPTION-AUTHORITY-SERVICE-20260810-01

Status: FROZEN / PRODUCT NOT STARTED
Risk: `PROTECTED`
Outcome: publish, revoke and exactly resolve auditable future-annuity draft exceptions without
changing the default instruction-first rule.

## Authority and dependencies

- `AGENTS.md`
- `docs/product/v8/domain-contract.md`
- `docs/product/v8/source-decision-registry.md`,
  `DEC-V8-FULL-BATCH-SCHEME-A-20260810`
- `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`, SHA-256
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`
- `V8-FULL-BATCH-CUSTOMER-DECISION-CURRENT-ADOPTION`
- `V8-FUTURE-ANNUITY-GATE-MANIFEST-ACTIVATION-CURRENT-ADOPTION`
- accepted decision-gate read service
- `V8-FUTURE-ANNUITY-EXCEPTION-CARRIER-SCHEMA-CURRENT-ADOPTION`
- accepted RBAC authority demonstrated by
  `V8-DECISION-GATE-SERVICE-API-VERTICAL-ADOPTION`,
  `V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-CURRENT-ADOPTION` and
  `V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-API-CURRENT-ADOPTION`

Scheme A fixes `DG-FEE-FUTURE-ANNUITY:GLOBAL` at `APPROVED_POLICY`, source version
`customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`. Client instruction remains required by
default and the initial exception set is empty. No missing or historical row is authority.

## Exact service interface

Create `backend/app/modules/system/future_annuity_exception_authority_service.py` with exact enum
types; raw strings and lookalikes are rejected.

```python
class FutureAnnuityExceptionScope(str, Enum):
    CLIENT = "CLIENT"
    CASE = "CASE"

class FutureAnnuityExceptionRecordType(str, Enum):
    PUBLISHED = "PUBLISHED"
    REVOKED = "REVOKED"

class FutureAnnuityExceptionDisposition(str, Enum):
    CREATED = "CREATED"
    REUSED = "REUSED"

@dataclass(frozen=True, slots=True, kw_only=True)
class PublishFutureAnnuityExceptionCommand:
    scope_type: FutureAnnuityExceptionScope
    scope_id: str
    effective_from: datetime
    effective_to: datetime
    record_version: str
    source_reference: str
    source_version: str
    reason: str
    confirmed_by: str
    published_at: datetime
    effective_at: datetime
    idempotency_key: str

@dataclass(frozen=True, slots=True, kw_only=True)
class RevokeFutureAnnuityExceptionCommand:
    target_publication_id: str
    record_version: str
    reason: str
    confirmed_by: str
    published_at: datetime
    effective_at: datetime
    idempotency_key: str

@dataclass(frozen=True, slots=True, kw_only=True)
class ResolveFutureAnnuityExceptionCommand:
    client_id: str
    case_id: str
    as_of: datetime

@dataclass(frozen=True, slots=True, kw_only=True)
class FutureAnnuityExceptionRecordResult:
    record_id: str
    record_type: FutureAnnuityExceptionRecordType
    target_publication_id: str | None
    record_version: str
    record_snapshot_hash: str
    disposition: FutureAnnuityExceptionDisposition

@dataclass(frozen=True, slots=True, kw_only=True)
class FutureAnnuityExceptionUseAttestation:
    gate_id: str
    gate_source_reference: str
    gate_source_version: str
    publication_id: str
    publication_snapshot_hash: str
    scope_type: FutureAnnuityExceptionScope
    scope_id: str
    client_id: str
    case_id: str
    effective_from: datetime
    effective_to: datetime
    record_version: str
    source_reference: str
    source_version: str
    confirmed_by: str
    published_at: datetime
    effective_at: datetime
    as_of: datetime

def publish_future_annuity_exception(
    command: PublishFutureAnnuityExceptionCommand, transaction: Session
) -> FutureAnnuityExceptionRecordResult: ...

def revoke_future_annuity_exception(
    command: RevokeFutureAnnuityExceptionCommand, transaction: Session
) -> FutureAnnuityExceptionRecordResult: ...

def resolve_future_annuity_exception(
    command: ResolveFutureAnnuityExceptionCommand, transaction: Session
) -> FutureAnnuityExceptionUseAttestation: ...
```

All DTOs require exact runtime types, canonical UUIDs, exact nonblank bounded strings and
UTC-naive datetimes. `effective_to` is mandatory and greater than `effective_from`. No ORM row,
implicit session or implicit clock is exposed.

## Permission, gate and scope rules

- Publication and revocation require an existing active `confirmed_by` user whose permissions
  from accepted `get_user_permissions` contain exactly `SystemParam.Edit`. No role-name, username,
  environment or superuser fallback exists. A later HTTP adapter must also inject authenticated
  `current_user.id` and parameter-bind `require_perm("SystemParam.Edit")`; it is not in this story.
- Every call resolves the exact current GLOBAL gate: mutations at `published_at`, resolution at
  `as_of`. Exact value, resolved scope, Scheme A source path and decision version must match.
  Gate validation precedes RBAC, idempotency and carrier reads, including replay.
- `CLIENT` maps `scope_id` only to carrier `client_id`; `CASE` maps it only to carrier `case_id`.
  The referenced row must exist. Resolution requires existing client and case rows and exact
  `Case.client_id == client_id`; null/mismatched relationships fail closed.
- No GLOBAL, wildcard, department, user, role, foreign-agent or inferred client scope is allowed.

## Time, overlap and revocation

A publication is usable exactly when `effective_from <= as_of < effective_to`,
`published_at <= as_of` and `effective_at <= as_of`. Its prospective usable segment is
`[max(effective_from, published_at, effective_at), effective_to)` and must be non-empty.

Publication rejects any non-empty usable-segment intersection with the same client, same case, or
between a client and a case whose persisted client matches. Boundary-touching half-open segments
are valid. There is no case-over-client precedence. Resolution independently rejects duplicate
same-scope candidates, simultaneous CLIENT/CASE candidates and any corrupt ambiguity.

Revocation targets exactly one canonical `PUBLISHED` row, copies its `source_reference` and
`source_version`, and appends one `REVOKED` row without changing the target. It suppresses the
target only when both revocation `published_at` and `effective_at` have arrived. A second
revocation conflicts; past attestations and drafts are never rewritten.

## Canonical audit, replay and transaction

Use the carrier's exact `FPMS_FUTURE_ANNUITY_DRAFT_EXCEPTION_V1` PUBLISHED/REVOKED key sets.
Serialize UTF-8 JSON with `ensure_ascii=False`, `sort_keys=True`, `separators=(",", ":")`,
`allow_nan=False`, and microsecond UTC-naive ISO timestamps; persist the lowercase SHA-256 of the
exact bytes. Replay and resolution require exact keys, canonical bytes, recomputed hash and full
column/scope/target/actor/time agreement. Corrupt data is never repaired or skipped.

Exact replay rechecks gate and mutation permission, then returns the original row as `REUSED`
without writing. Changed input under one key, record-version collision, second target revocation,
overlap or unique race is `409`; race recovery returns `REUSED` only after full canonical match.

Reject caller sessions with pending new/dirty/deleted state. Each mutation uses one nested
savepoint, may flush, and never commits, rolls back or closes the caller session. Forced failure
and caller rollback leave no row. Resolution is read-only.

## Error contract

- `400 FUTURE_ANNUITY_EXCEPTION_INPUT_INVALID`: invalid command/type/enum/string/UUID/time/interval,
  before connection or query.
- `404 FUTURE_ANNUITY_EXCEPTION_NOT_FOUND`: missing actor/client/case/target publication, or no
  currently usable exception.
- `409 FUTURE_ANNUITY_EXCEPTION_TRANSACTION_DIRTY`: pending caller state.
- `409 FUTURE_ANNUITY_EXCEPTION_CONFLICT`: inactive/unauthorized actor, wrong gate result,
  relationship mismatch, overlap/ambiguity, corrupt lineage/hash, changed replay or race.
- Accepted decision-gate failures preserve their exact `409` code/details. Failure never creates a
  default exception or lower-authority fallback.

## Non-goals and successor

No API/UI, permission/role/seed/default, migration/model/RBAC/gate change, draft, instruction,
amount, reduction, deadline, PayList, payment, receipt, lifecycle or legal-state mutation. No
exception-use activity is written here.

Ordinal 213 `FPMS-V8-FUTURE-ANNUITY-AUTO-DRAFT-POLICY-20260712-01` remains the successor. After
this story is accepted, ordinal 213 must be re-frozen and solely owns its distinct
future-annuity-exception `FeeDraftAuthority`, deep obligation validation, draft activity carrying
publication ID/hash/attestation time, exact draft replay and later explicit-PAY compatibility.
Neither story may forge PAY or reuse reviewed-notice authority.

## Paths, tests, rollback and adoption

Implementation allowlist:

- this task file;
- `backend/app/modules/system/future_annuity_exception_authority_service.py`;
- `backend/tests/test_v8_future_annuity_exception_authority_service.py`.

All carrier/model/migration, RBAC, gate, case/client, API, annuity, fee, task, manifest and ledger
paths are read-only during implementation. SQLite-writing tests are serialized.

Verification:

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_future_annuity_exception_authority_service.py`
- regressions: `cd backend && .venv/bin/pytest -q tests/test_v8_future_annuity_exception_carrier_schema.py tests/test_v8_decision_gate_read_service.py tests/test_system_params.py`
- scoped Ruff: `cd backend && .venv/bin/ruff check app/modules/system/future_annuity_exception_authority_service.py tests/test_v8_future_annuity_exception_authority_service.py`
- scoped diff: `git diff --check --` the three allowlisted paths.

Rollback reverts only the exact implementation commit/range and creates no compensating data.
Acceptance requires the focused checks, exact commit/range, one independent High review with zero
P0/P1/P2 findings, integration of that reviewed range, and controller adoption as
`V8-FUTURE-ANNUITY-EXCEPTION-AUTHORITY-SERVICE-CURRENT-ADOPTION` in the coverage ledger. A
byte-changing rebase or later override invalidates prior verification and review.
