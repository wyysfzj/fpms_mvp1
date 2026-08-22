# FPMS-V8-GRANT-EVIDENCE-REVIEW-SERVICE-20260712-01

Status: CONTRACT RE-FROZEN / READY FOR IMPLEMENTATION
Risk class: `PROTECTED`
Runbook: `P0-prereq-heavy-story`
Catalog ordinal: `204`

## Authority and prerequisites

- Scheme A customer source SHA-256
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Accepted current grant-evidence ingestion service and adoption.
- Accepted current grant manual-review role carrier/service and adoption.

The prior task text did not bind review to the accepted current second-reviewer role, did not
freeze replay or concurrent-update behavior, and did not define how the raw candidate bytes remain
authoritative. This successor closes those gaps without dispatching a legal-state transition.

## Exact closure and public interface

Create `backend/app/modules/documents/grant_evidence_review_service.py` with exact frozen DTOs:

```python
class GrantEvidenceReviewDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class GrantEvidenceReviewDisposition(str, Enum):
    CHANGED = "CHANGED"
    REUSED = "REUSED"


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewGrantEvidenceCandidateCommand:
    candidate_id: str
    decision: GrantEvidenceReviewDecision
    reviewer_id: str
    reviewed_at: datetime
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewGrantEvidenceCandidateResult:
    candidate_id: str
    evidence_version_id: str
    review_status: str
    reviewer_id: str
    reviewed_at: datetime
    candidate_snapshot_hash: str
    review_role_config_id: str
    review_role_config_snapshot_hash: str
    disposition: GrantEvidenceReviewDisposition


def review_grant_evidence_candidate(
    command: ReviewGrantEvidenceCandidateCommand,
    transaction: Session,
) -> ReviewGrantEvidenceCandidateResult: ...
```

Raw strings/lookalike enums are rejected. IDs are canonical UUIDs; `reviewed_at` is UTC-naive;
`reason` is nonblank, trimmed, NUL-free and at most 4096 characters. The caller session must have
no pending new, dirty or deleted ORM state before service work begins.

## Fail-closed candidate and reviewer authority

Load exactly one `GrantEvidenceCandidate` by `candidate_id`. Its identifiers and timestamps must
be canonical, its review tuple must be either exact PENDING or exact terminal, and `reviewed_at`
must not precede `proposed_at`. The exact stored UTF-8 candidate JSON must be canonical
(`ensure_ascii=False`, `sort_keys=True`, separators `(",", ":")`, `allow_nan=False`), have schema
`CNIPA_GRANT_EVIDENCE_CANDIDATE_V1`, and contain only `schema_version`, `evidence_scope`, `facts`
and `conflicts`. Reapply the ingestion contract's exact ordered, unique, nonblank raw fact/conflict
rules; recompute the candidate SHA-256. `conflict_snapshot` must remain NULL when conflicts are
empty and otherwise equal the exact canonical conflicts array. The acquisition snapshot/hash must
also remain exact canonical JSON/SHA-256 and its case, document, evidence, source, scope, proposal,
reference, method and acquisition-time bindings must equal the row. Any missing, ambiguous,
noncanonical, corrupted or cross-bound state is 409/no write.

Resolve the accepted GLOBAL manual-review role configuration at `reviewed_at` using
`resolve_grant_manual_review_role_config`. The reviewer must be an active actual `T_User` currently
bound to `manual_review_second_reviewer_role_id` and must differ from `proposed_by`. A missing,
revoked, future, stale or invalid configuration or binding is 409/no write. Do not infer an
administrator, document reviewer, proposer, acquirer or verifier as the second reviewer.

## Mutation, replay and concurrency

For an exact PENDING row, perform one compare-and-swap update guarded by `id`,
`review_status == PENDING` and all three review fields being NULL. Set only `review_status`, `reviewer_id`,
`reviewed_at`, `review_reason` and `updated_at`; raw facts/conflicts, acquisition/source/evidence
lineage, proposal fields and every other row remain byte-for-byte unchanged. Establish SQLite's
outer transaction when necessary, execute the update inside exactly one nested savepoint, and
never commit, roll back or close the caller session.

An exact terminal replay returns `REUSED` only when decision, reviewer, reviewed time and reason
all equal the command and the candidate and current reviewer authority still validate. Any changed
repeat, inconsistent terminal tuple, lost compare-and-swap, integrity failure, duplicate or race is
`GRANT_EVIDENCE_REVIEW_CONFLICT`/409 with no partial residue. Malformed input is
`GRANT_EVIDENCE_REVIEW_INPUT_INVALID`/400. A successful first transition returns `CHANGED`.

## Explicit non-closure

No endpoint/UI/schema/migration, ingestion/source/role publication or mutation, current-source
resolution, legal-state dispatch, grant confirmation, lifecycle/deadline, document/evidence/case
mutation, activity/event/outbox creation, fee, payment or receivable behavior. Review records only
the manual decision on the existing candidate; APPROVED is not itself a grant-state transition.

## Allowed files

- this task file;
- `backend/app/modules/documents/grant_evidence_review_service.py`;
- `backend/tests/test_v8_grant_evidence_review_service.py`.

## Frozen acceptance matrix

1. A canonical PENDING candidate plus a distinct active current configured second reviewer makes
   exactly one APPROVED or REJECTED transition while preserving all raw bytes and causing no legal
   or adjacent side effect.
2. Self-review, inactive/unbound reviewer and missing/revoked/future/stale role configuration fail
   409/no write.
3. Missing, corrupt, noncanonical, cross-bound or inconsistent candidate/acquisition/review state
   fails 409/no write; malformed command input fails 400 before query or mutation.
4. Exact terminal replay is REUSED after current authority validation; changed replay is 409.
5. Lost compare-and-swap and injected write failure leave no partial residue.
6. Caller rollback removes the review transition; service never commits, rolls back or closes the
   transaction and never changes legal/lifecycle/document/evidence/case/fee/payment state.

## Verification

- Focused RED/GREEN pytest for the named review service test.
- Scoped Ruff and exact three-path diff-check.
- One independent PROTECTED reviewer reviews the exact implementation range and reruns decisive
  checks.
- PASS requires `P0/P1/P2 = 0/0/0`; no Full or release gate belongs here.
