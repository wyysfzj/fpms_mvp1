# FPMS-V8-GRANT-OFFICIAL-COPY-VERIFICATION-SERVICE-20260810-01

Status: FROZEN / READY FOR IMPLEMENTATION
Risk class: `PROTECTED`
Runbook: `P0-prereq-heavy-story`

## Authority and prerequisites

- Scheme A customer source SHA-256
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Accepted grant source carrier/service/API.
- Accepted grant manual-review role carrier/service/API.
- Accepted official-copy verification carrier schema at commit `f4d593b`.

The institution administrator configures all five duty roles and selects only reviewed/activated
CNIPA sources. Missing or invalid configuration disables the affected function. First and second
verification must be performed by different actual active users. A terminal verification event is
necessary lineage but is not a legal-status decision.

## Exact closure

Create `backend/app/modules/documents/grant_official_copy_verification_service.py` with:

```python
class GrantOfficialCopyEventType(str, Enum):
    ACQUIRED = "ACQUIRED"
    FIRST_VERIFIED = "FIRST_VERIFIED"
    SECOND_VERIFIED = "SECOND_VERIFIED"


class GrantOfficialCopyDisposition(str, Enum):
    CREATED = "CREATED"
    REUSED = "REUSED"


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordGrantOfficialCopyEventCommand:
    evidence_version_id: str
    evidence_scope: GrantEvidenceScope
    event_type: GrantOfficialCopyEventType
    actor_id: str
    action_at: datetime
    reason: str
    original_reference: str | None
    expected_current_event_id: str | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantOfficialCopyEventResult:
    event_id: str
    evidence_version_id: str
    evidence_scope: GrantEvidenceScope
    event_type: GrantOfficialCopyEventType
    source_config_id: str
    source_record_id: str
    role_config_id: str
    event_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantOfficialCopyDisposition


def record_grant_official_copy_event(
    command: RecordGrantOfficialCopyEventCommand,
    transaction: Session,
) -> GrantOfficialCopyEventResult: ...
```

Raw strings and lookalike enums are rejected. IDs are canonical lowercase UUID strings; action
time is UTC-naive. Reason, reference and idempotency are nonblank, trimmed and NUL-free; reason is
at most 4096 characters, reference at most 512 and idempotency at most 128. `ACQUIRED` requires a
reference and null expected current. Both verifier events require null reference and one exact
expected-current UUID.

## Evidence, source and role rules

The evidence version must exist, remain current for its lineage, have `role=RAW_ATTACHMENT`,
`state=FINAL`, `review_state=PENDING`, null reviewer/reviewed/final-submitted fields, a valid stored
content hash, and an attachment that still belongs to its document. No evidence/document row is
created or mutated.

For every action, before writes, resolve the exact source for `evidence_scope` and `action_at` with
`resolve_grant_evidence_source`, and the exact GLOBAL duty-role configuration at `action_at` with
`resolve_grant_manual_review_role_config`. Resolver failure is a 409 with zero write. The actor
must be active and currently assigned to the configured role for the requested stage:

- `ACQUIRED` -> `official_copy_acquirer_role_id`;
- `FIRST_VERIFIED` -> `first_verifier_role_id`;
- `SECOND_VERIFIED` -> `second_verifier_role_id`.

First and second verifier IDs must differ. No additional acquirer/verifier separation is inferred.
Verifier events must retain the acquisition event's exact evidence content hash, original
reference, acquisition method, source record/configuration IDs and source hashes. The freshly
resolved source must match those stored acquisition-lineage bytes; a changed source requires a new
official raw evidence version and acquisition chain. The role configuration is resolved and bound
independently at each stage, so an audited role reassignment does not rewrite earlier events.

## Exact progression, canonical bytes and replay

The only progression is `ACQUIRED -> FIRST_VERIFIED -> SECOND_VERIFIED`. There is at most one
current row identified by `GRANT_OFFICIAL_COPY|{evidence_version_id}`. Acquisition requires no
current row. Each verifier requires its exact expected current row, same evidence/scope, canonical
stored lineage and the immediately preceding stage. Second verification additionally requires a
different actual user from the first verifier.

Canonical event JSON uses UTF-8, `ensure_ascii=False`, `sort_keys=True`, separators `(",", ":")`,
`allow_nan=False`; action time is `isoformat(timespec="microseconds")`. It contains exactly:
`schema`, `evidence_version_id`, `source_config_id`, `source_record_id`, `role_config_id`,
`evidence_scope`, `event_type`, `actor_id`, `action_at`, `reason`, `original_reference`,
`acquisition_method_snapshot`, `evidence_content_hash`, `source_config_snapshot_hash`,
`source_snapshot_hash`, `role_config_snapshot_hash`, and `predecessor_event_id`. `schema` is
`CNIPA_GRANT_OFFICIAL_COPY_VERIFICATION_EVENT_V1`; the stored hash is lowercase SHA-256 of the
exact JSON text.

An exact idempotency replay returns `REUSED` only after the same resolvers and personnel checks
still succeed and every stored command/derived/canonical byte matches. Any mismatch, corrupt row,
wrong stage/current/predecessor, duplicate or ambiguous state is
`GRANT_OFFICIAL_COPY_EVENT_CONFLICT`/409 with no write. Malformed input is
`GRANT_OFFICIAL_COPY_EVENT_INPUT_INVALID`/400.

Creation uses one nested savepoint. A verifier atomically clears the exact predecessor current
pointer and inserts the new current event; rowcount must be one. The caller owns commit, rollback
and close. SQLite correctness must not depend on `RETURNING`.

## Non-closure

No endpoint/UI/schema/migration/source or role publication/default/seed; no candidate ingestion or
review; no evidence/document mutation; no legal status, lifecycle, deadline, fee or payment write;
no generic workflow/event abstraction. Second verification alone never confirms grant.

## Allowed files

- this task file;
- `backend/app/modules/documents/grant_official_copy_verification_service.py`;
- `backend/tests/test_v8_grant_official_copy_verification_service.py`.

## Frozen acceptance matrix

1. A valid acquisition and exact two-verifier sequence writes three canonical events, keeps one
   current pointer, binds current source and per-stage role configuration, and returns CREATED.
2. Every stage requires the exact active configured duty membership; missing/revoked/future,
   source mismatch, inactive/unbound actor and missing personnel/configuration fail 409/no write.
3. Wrong predecessor/current/stage/evidence/scope, same first/second actual user, corrupt lineage or
   canonical hashes, and invalid evidence-version/attachment state fail closed.
4. Exact replay returns the same event as REUSED; changed replay and unique/CAS races return 409
   without partial pointer movement or residue.
5. Caller rollback removes the event/pointer change; injected flush failure leaves the predecessor
   current; the service never commits or rolls back.
6. No candidate, evidence, document, case lifecycle/legal status, deadline, fee or payment row is
   created or changed.

## Verification

- Focused RED/GREEN pytest for the named service test.
- Affected source resolver, role resolver and carrier-schema regressions.
- Scoped Ruff and exact two-path diff-check.
- One independent High reviewer reviews the exact implementation range and reruns decisive checks.
- PASS requires `P0/P1/P2 = 0/0/0`; no Full or release gate belongs here.
