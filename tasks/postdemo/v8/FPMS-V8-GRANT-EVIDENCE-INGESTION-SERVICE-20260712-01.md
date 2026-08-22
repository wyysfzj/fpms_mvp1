# FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01

Status: CONTRACT RE-FROZEN / READY FOR IMPLEMENTATION
Risk class: `PROTECTED`
Runbook: `P0-prereq-heavy-story`
Catalog ordinal: `200`

## Authority and prerequisites

- Scheme A customer source SHA-256
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Accepted evidence-version, grant-source and institution duty-role carriers/services.
- Accepted official-copy `ACQUIRED -> FIRST_VERIFIED -> SECOND_VERIFIED` carrier/service/API.

The prior contract incorrectly allowed `proposed_by` to stand in the acquisition snapshot without
proving the separate official-copy acquirer and two-verifier chain. This successor removes all
caller-supplied acquisition facts. A candidate may be created only from the exact current terminal
verification event, while the candidate proposer is separately checked against the configured
manual-review proposer role.

## Exact closure and public interface

Create `backend/app/modules/documents/grant_evidence_ingestion_service.py` with exact frozen DTOs:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class GrantEvidenceFact:
    name: str
    raw_value: str


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantEvidenceConflict:
    name: str
    raw_values: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class IngestGrantEvidenceCandidateCommand:
    case_id: str
    document_id: str
    evidence_version_id: str
    evidence_scope: GrantEvidenceScope
    expected_terminal_event_id: str
    proposed_by: str
    proposed_at: datetime
    facts: tuple[GrantEvidenceFact, ...]
    conflicts: tuple[GrantEvidenceConflict, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class IngestGrantEvidenceCandidateResult:
    candidate_id: str
    evidence_version_id: str
    terminal_event_id: str
    source_config_id: str
    source_record_id: str
    proposal_role_config_id: str
    evidence_scope: GrantEvidenceScope
    acquisition_snapshot_hash: str
    candidate_snapshot_hash: str
    review_status: str
    disposition: str  # CREATED | REUSED


def ingest_grant_evidence_candidate(
    command: IngestGrantEvidenceCandidateCommand,
    transaction: Session,
) -> IngestGrantEvidenceCandidateResult: ...
```

Raw strings/lookalike enums are rejected. IDs are canonical UUIDs; `proposed_at` is UTC-naive.
Fact/conflict strings are nonblank, trimmed, NUL-free and at most 4096 characters. Facts are
nonempty, names unique and sorted by `(name, raw_value)`. Conflicts are sorted by name, names are
unique and present in facts, and each has at least two distinct nonblank raw values already sorted
lexically. Reject rather than silently reorder.

## Fail-closed official-copy and proposer authority

The evidence version must be the exact current `RAW_ATTACHMENT`, `FINAL`, `PENDING` version for the
command case/document; reviewer/review/final-submission fields are null, content hash is valid and
the referenced attachment belongs to the same document with the same content hash.

There must be exactly one current official-copy event with identity
`GRANT_OFFICIAL_COPY|{evidence_version_id}`. It must equal `expected_terminal_event_id`, have stage
`SECOND_VERIFIED`, same evidence/scope/content hash, and resolve a complete canonical
`ACQUIRED -> FIRST_VERIFIED -> SECOND_VERIFIED` chain. Recompute each exact V1 event JSON/hash;
require exact predecessor IDs, stable source record/config IDs and hashes, original reference,
acquisition method and evidence content hash across the chain, plus distinct first/second actual
users. Any missing, duplicate, corrupt or nonterminal lineage is 409/no write.

Each event's referenced duty-role configuration must still exist, match its stored snapshot hash,
have been ACTIVE and effective at that event's action time, and have been published no later than
the action. This is historical lineage validation only; do not apply the latest role configuration
retroactively to acquisition or verifier events.

Resolve the exact GLOBAL duty-role configuration at `proposed_at` using
`resolve_grant_manual_review_role_config`. The proposer must be an active actual user currently
bound to `manual_review_proposer_role_id`. Missing/revoked/future/invalid configuration or binding
is 409/no write. Do not infer the acquirer, a verifier or a generic document editor as proposer.

Read the source record/config referenced by the accepted event chain. They must still exist, match
the stored scope and snapshot hashes, and represent reviewed activated CNIPA authority. The source
must have been reviewed, activated and effective, and the configuration ACTIVE, published and
effective, no later than the acquisition action. A durable source record may now be ACTIVE or
RETIRED and its historical ACTIVE configuration may no longer own the current pointer; later
retirement/revocation does not rewrite the already verified raw copy. No revoked configuration,
current-source fallback or substitution is allowed.

## Exact canonical candidate bytes

Canonical JSON uses UTF-8, `ensure_ascii=False`, `sort_keys=True`, separators `(",", ":")`,
`allow_nan=False`; datetimes are UTC-naive `isoformat(timespec="microseconds")`; hashes are lowercase
SHA-256 of exact stored text.

`acquisition_snapshot`, schema `CNIPA_GRANT_EVIDENCE_ACQUISITION_V2`, contains exactly:

- `schema_version`, `case_id`, `document_id`, `attachment_id`, `evidence_version_id`,
  `evidence_content_hash`, `evidence_scope`;
- `acquisition_event_id`, `acquisition_event_snapshot_hash`, `acquired_by`, `acquired_at`,
  `acquisition_reason`;
- `first_verification_event_id`, `first_verification_event_snapshot_hash`, `first_verified_by`,
  `first_verified_at`, `first_verification_reason`;
- `terminal_verification_event_id`, `terminal_verification_event_snapshot_hash`,
  `second_verified_by`, `second_verified_at`, `second_verification_reason`;
- `source_config_id`, `source_config_snapshot_hash`, `source_record_id`, `source_version`,
  `source_snapshot_hash`, `original_reference`, `acquisition_method`;
- `proposal_role_config_id`, `proposal_role_config_snapshot_hash`, `proposed_by`, `proposed_at`.

`candidate_snapshot`, schema `CNIPA_GRANT_EVIDENCE_CANDIDATE_V1`, contains exactly
`schema_version`, `evidence_scope`, `facts` (ordered exact `name/raw_value` objects) and `conflicts`
(ordered exact `name/raw_values` objects). `conflict_snapshot` is NULL for no conflicts; otherwise
it is canonical JSON of exactly the conflicts array. Conflicts remain raw evidence and never select
or normalize legal status.

Persist exactly one `GrantEvidenceCandidate`: source/evidence/case/document IDs from validated
lineage; source version/reference/method and `acquired_at` from acquisition authority; V2
acquisition snapshot/hash; candidate snapshot/hash; authenticated proposer/time; `PENDING`, with no
reviewer/review time/reason. The database unique evidence-version identity controls replay.

Exact replay returns `REUSED` only when every stored field and canonical byte/hash matches the newly
derived command and still-valid authority. Changed replay, duplicate/ambiguous state, corruption or
race is `GRANT_EVIDENCE_CANDIDATE_CONFLICT`/409. Malformed input is
`GRANT_EVIDENCE_CANDIDATE_INPUT_INVALID`/400. Creation uses one nested savepoint and flush, never
commit/rollback; caller owns the transaction.

## Non-closure

No endpoint/UI/schema/migration, current-source resolution, source/role publication/default/seed,
candidate read/review, legal-state dispatch, lifecycle/deadline, document/evidence mutation, fee or
payment behavior. Candidate PENDING and terminal copy verification do not confirm grant.

## Allowed files

- this task file;
- `backend/app/modules/documents/grant_evidence_ingestion_service.py`;
- `backend/tests/test_v8_grant_evidence_ingestion_service.py`.

## Frozen acceptance matrix

1. Exact terminal verified chain plus configured active proposer creates one canonical PENDING
   candidate bound to distinct acquisition/verifier/proposer facts, with zero legal-state effect.
2. Nonterminal/wrong-current/cross-evidence/cross-scope/corrupt event chains, same first/second user,
   missing historical authority rows or mismatched hashes fail 409/no write.
3. Missing/revoked/future role configuration and inactive/unbound proposer fail 409/no write.
4. Malformed/unsorted fact/conflict input and invalid evidence/attachment state fail closed.
5. Exact replay is REUSED; changed replay and concurrent duplicate are 409 without residue.
6. Caller rollback removes only the candidate; injected flush failure leaves no residue; service
   never commits/rolls back and never changes legal/lifecycle/document/evidence/fee/payment facts.

## Verification

- Focused RED/GREEN pytest for the named ingestion service test.
- Official-copy service/schema, role resolver and source carrier regressions.
- Scoped Ruff and exact two-path diff-check.
- One independent High reviewer reviews the exact implementation range and reruns decisive checks.
- PASS requires `P0/P1/P2 = 0/0/0`; no Full or release gate belongs here.
