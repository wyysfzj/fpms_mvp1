# FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SERVICE-20260810-01

Status: FROZEN CANDIDATE / READY FOR INDEPENDENT HIGH REVIEW
Risk class: `PROTECTED`
Executor: Backend Developer

## Authority and prerequisites

- `AGENTS.md`
- `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`
  (`e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`)
- decision version `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`
- `DG-GRANT-MANUAL-REVIEW:GLOBAL` is `APPROVED_POLICY / CONFIG_REQUIRED`
- accepted decision-gate read service
- `V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SCHEMA-CURRENT-ADOPTION`

Missing, revoked, future, expired, malformed, ambiguous or personnel-incomplete authority disables
only the affected grant-evidence action with `409 / NO WRITE / NO LEGAL-STATE CHANGE`.

## Exact closure

Create `backend/app/modules/system/grant_manual_review_role_service.py` with exact keyword-only,
frozen DTOs and three synchronous functions:

```python
class GrantManualReviewRoleDisposition(str, Enum):
    CREATED = "CREATED"
    REUSED = "REUSED"

@dataclass(frozen=True, slots=True, kw_only=True)
class PublishGrantManualReviewRoleConfigCommand:
    official_copy_acquirer_role_id: str
    first_verifier_role_id: str
    second_verifier_role_id: str
    manual_review_proposer_role_id: str
    manual_review_second_reviewer_role_id: str
    config_version: str
    effective_from: datetime
    effective_to: datetime | None
    confirmed_by: str
    published_at: datetime
    expected_current_config_id: str | None
    idempotency_key: str

@dataclass(frozen=True, slots=True, kw_only=True)
class RevokeGrantManualReviewRoleConfigCommand:
    config_version: str
    effective_from: datetime
    confirmed_by: str
    published_at: datetime
    expected_current_config_id: str
    idempotency_key: str

@dataclass(frozen=True, slots=True, kw_only=True)
class ResolveGrantManualReviewRoleConfigCommand:
    as_of: datetime

@dataclass(frozen=True, slots=True, kw_only=True)
class GrantManualReviewRoleConfigResult:
    config_id: str
    config_status: str
    config_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantManualReviewRoleDisposition

@dataclass(frozen=True, slots=True, kw_only=True)
class GrantManualReviewRoleResolution:
    gate_id: str
    config_id: str
    config_snapshot_hash: str
    official_copy_acquirer_role_id: str
    first_verifier_role_id: str
    second_verifier_role_id: str
    manual_review_proposer_role_id: str
    manual_review_second_reviewer_role_id: str
    effective_from: datetime
    effective_to: datetime | None
```

Functions:

- `publish_grant_manual_review_role_config(command, transaction)`;
- `revoke_grant_manual_review_role_config(command, transaction)`;
- `resolve_grant_manual_review_role_config(command, transaction)`.

## Exact authority and validation boundary

All calls require an exact SQLAlchemy `Session` with no dirty/new/deleted caller state. Strings
are exact, trimmed, nonblank, NUL-free and within carrier lengths; IDs are canonical UUID strings;
datetimes are UTC-naive; intervals are half-open and valid. Raw lookalike commands/enums fail
`400 GRANT_MANUAL_REVIEW_ROLE_INPUT_INVALID` before a connection, gate resolution or write.

Every operation first resolves the exact current Scheme A decision through
`resolve_decision_gate` using:

- gate `DG-GRANT-MANUAL-REVIEW`;
- scope `GLOBAL`;
- decision `APPROVED_POLICY`;
- exact source path and decision version above;
- `published_at` for publication and revocation, and `as_of` for resolution. `effective_from`
  defines only the configuration's applicability interval and is never substituted for the
  decision-gate read instant.

This gate check precedes idempotency replay lookup as well as a new write. An exact publication or
revocation replay therefore uses its original command `published_at` and cannot bypass missing,
revoked, wrong-source or not-yet-effective authority by relying on `effective_from`.

Any mismatch is `409 GRANT_MANUAL_REVIEW_ROLE_CONFLICT`. No case/customer/role-name/environment
fallback is permitted.

## Canonical publication and current lineage

Canonical JSON uses UTF-8, `ensure_ascii=False`, `sort_keys=True`, separators `(",", ":")`,
`allow_nan=False`; timestamps use UTC-naive ISO-8601 with microseconds. The snapshot has exactly
the schema task's frozen keys and schema `FPMS_GRANT_MANUAL_REVIEW_ROLE_CONFIG_V1`; its lowercase
SHA-256 is persisted.

Publication appends one `ACTIVE` row. Revocation revalidates the exact current `ACTIVE` predecessor,
copies all five role IDs, appends one current `REVOKED` row and clears only the predecessor current
key. Both use expected-current CAS inside one nested savepoint and never commit/rollback/close the
caller session. Exact idempotent replay returns `REUSED`; changed payload, corrupted replay,
duplicate/ambiguous current, predecessor mismatch or concurrent CAS returns `409` with no residue.
A current revoked row shadows history; resolver never falls back to an older active row.

## Role/personnel readiness

Before publishing and on every active resolution, query exact role IDs and current RBAC
memberships. All five roles must exist. Each configured role must have at least one active
`t_user` member through `t_user_role`. There must exist at least one distinct actual-user pair
across first/second verifier roles and at least one distinct pair across proposer/second-reviewer
roles. The same role ID in two slots is valid only when that role contains at least two active
users. Do not select a user or return a fallback user; this service proves readiness only.

Revocation validates the predecessor's persisted canonical bytes, current identity and copied role
IDs, but does not require personnel readiness; administrators must be able to revoke a configuration
whose memberships have become unusable. Resolver revalidates current canonical bytes/hash,
predecessor chain, `ACTIVE` status, effective interval and personnel readiness.

Later action services must still prove the authenticated actors are active members of their exact
configured roles and enforce first verifier != second verifier and proposer != second reviewer.
This service does not authorize or record an operational action.

## Non-closure

No API/router/schema/permission/UI; no role/user/membership/default/seed; no official-copy or
candidate evidence mutation; no acquisition/review actor selection; no document, lifecycle, legal
status, deadline, fee, draft or payment change; no migration/model/registry edit; no generic RBAC
refactor; no coverage/release edit.

## Allowed files

- this task file;
- `backend/app/modules/system/grant_manual_review_role_service.py`;
- `backend/tests/test_v8_grant_manual_review_role_service.py`.

All inherited source/schema/decision-gate tests are read-only. SQLite tests are serialized.

## Frozen acceptance matrix

1. Valid exact gate, five roles and viable active-user pairs publish one canonical current ACTIVE
   row; same role IDs with two active users are accepted.
2. Exact replay returns the same row; changed input, idempotency or expected-current conflicts,
   concurrent CAS and duplicate/ambiguous persisted rows fail `409` without residue.
3. Missing/inactive role membership, a one-user same-role pair, missing gate, revoked/future/wrong
   source/version/value/scope gate, invalid interval/input and dirty caller state fail before write.
   A gate whose effective time falls strictly between `published_at` and `effective_from` is not
   effective for publication/revocation or their replay; resolution independently uses `as_of`.
4. Resolution returns only one current effective ACTIVE configuration and exact role IDs; corrupt
   snapshot/hash/key/status/interval/predecessor/membership state fails closed with no fallback.
5. Revocation copies the five IDs, advances current to REVOKED, permits unusable current
   memberships, exact-replays read-only, and makes resolution fail without old-row fallback.
6. Forced fault and caller rollback leave no successor/current-pointer residue. Service calls no
   commit, rollback or close and changes no legal/lifecycle/evidence/fee fact.

## Verification

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_manual_review_role_service.py`
- Schema/decision regressions:
  `cd backend && .venv/bin/pytest -q tests/test_v8_grant_manual_review_role_carrier_schema.py tests/test_v8_decision_gate_read_service.py`
- Ruff check-only:
  `cd backend && .venv/bin/ruff check app/modules/system/grant_manual_review_role_service.py tests/test_v8_grant_manual_review_role_service.py`
- Scope:
  `git diff --check -- backend/app/modules/system/grant_manual_review_role_service.py backend/tests/test_v8_grant_manual_review_role_service.py tasks/postdemo/v8/FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SERVICE-20260810-01.md`

One independent High reviewer must review the exact implementation commit/range and independently
rerun the decisive checks. PASS requires `P0/P1/P2 = 0/0/0`. No broad/release gate belongs here.
