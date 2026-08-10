# FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01

Status: CONTRACT RE-FROZEN / READY FOR IMPLEMENTATION
Risk class: `PROTECTED`
Runbook: `P0-shared-service-story`
Catalog ordinal: `202`

## Authority and prerequisites

- Scheme A SHA-256
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Accepted ingestion service implementation tip
  `cada0a256b2170eab934b5a3a55711880abd1466` and its current adoption.

This story is a read-only projection of persisted candidate truth. It never resolves legal status,
chooses among conflicts or substitutes a current source for the historical source lineage.

## Exact closure and public interface

Extend `backend/app/modules/documents/grant_evidence_ingestion_service.py` with exact frozen DTOs:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class ListGrantEvidenceCandidatesCommand:
    document_id: str
    read_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantEvidenceCandidateRead:
    candidate_id: str
    case_id: str
    document_id: str
    evidence_version_id: str
    terminal_event_id: str
    source_config_id: str
    source_record_id: str
    source_version: str
    original_reference: str
    acquisition_method: str
    acquired_at: datetime
    evidence_scope: GrantEvidenceScope
    proposal_role_config_id: str
    proposed_by: str
    proposed_at: datetime
    review_status: str
    reviewer_id: str | None
    reviewed_at: datetime | None
    review_reason: str | None
    acquisition_snapshot_hash: str
    candidate_snapshot_hash: str
    facts: tuple[GrantEvidenceFact, ...]
    conflicts: tuple[GrantEvidenceConflict, ...]


def list_grant_evidence_candidates(
    command: ListGrantEvidenceCandidatesCommand,
    transaction: Session,
) -> tuple[GrantEvidenceCandidateRead, ...]: ...
```

`document_id` is a canonical UUID and `read_at` is UTC-naive. Require a clean caller-owned Session
and use `no_autoflush`; never flush, commit or rollback. Resolve the exact confirmed
`DG-GRANT-EVIDENCE-SOURCE:GLOBAL` decision at `read_at`; missing/revoked/future/corrupt authority is
409. A missing document is `GRANT_EVIDENCE_DOCUMENT_NOT_FOUND`/404. An existing document with no
candidates returns an empty tuple.

Read candidates only for that document, ordered by `(proposed_at, id)`. Every row must have
canonical UUIDs, UTC-naive datetimes, a valid scope and exact review tuple: PENDING has no reviewer,
time or reason; APPROVED/REJECTED has all three and reviewer differs from proposer. Required text is
nonblank, trimmed and NUL-free; stored hashes are lowercase SHA-256.

Recompute and require the exact stored acquisition/candidate snapshot hashes. Both JSON objects
must have exactly the accepted V2/V1 key sets. Bind acquisition snapshot case/document/evidence,
source record/config/version, original reference, acquisition method/time, scope, proposer/time and
stored hashes back to the candidate columns. Extract only the terminal verification event ID and
proposal role-config ID after canonical UUID validation. Bind candidate snapshot scope and exact
ordered facts/conflicts; apply the ingestion input invariants again. `conflict_snapshot` must be
NULL for no conflicts or exact canonical JSON of the conflicts array otherwise. Any malformed,
ambiguous or divergent persisted state is `GRANT_EVIDENCE_CANDIDATE_CONFLICT`/409; do not skip it.

The result exposes raw facts/conflicts and review facts only. It does not infer a legal result,
normalize conflict values, query the current source, or require an old historical source/config to
remain current.

## Non-closure

No endpoint/schema/UI/migration, candidate create/review, source/role publication, official-copy
write, legal-state/lifecycle/deadline dispatch, document/evidence mutation, fee or payment behavior.

## Allowed files

- this task file;
- `backend/app/modules/documents/grant_evidence_ingestion_service.py`;
- `backend/tests/test_v8_grant_evidence_candidate_read_service.py`.

## Frozen acceptance matrix

1. Existing document plus zero/one/multiple valid candidates returns a deterministic exact tuple
   with historical source, proposer/reviewer/review and raw conflict facts.
2. Missing document is 404; malformed input/current gate failure is 400/409; all are no-write.
3. Corrupt hash/JSON/key set, snapshot-column divergence, invalid review tuple, invalid ordering or
   conflict data is 409 and the entire read fails closed.
4. Read never flushes/commits/rolls back and changes no legal/lifecycle/document/evidence/fee fact.

## Verification

- Focused RED/GREEN pytest for the named read-service test.
- Ingestion service and source decision-gate regressions.
- Scoped Ruff and exact two-path implementation diff-check.
- Independent High review of the exact implementation range; PASS requires P0/P1/P2 `0/0/0`.
