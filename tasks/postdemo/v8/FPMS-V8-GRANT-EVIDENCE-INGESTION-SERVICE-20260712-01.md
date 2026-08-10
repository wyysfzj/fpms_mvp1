# FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01

Status: CONTRACT RE-FROZEN / READY FOR INDEPENDENT HIGH REVIEW
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `200`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `708`
- Expected manifest phase: `deferred`
- Customer gate requirement: `DG-GRANT-EVIDENCE-SOURCE[GLOBAL]`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Resolve the exact current reviewed/active CNIPA source and `GLOBAL` configuration for one
`GRANT_ANNOUNCEMENT` or `PATENT_REGISTER` acquisition before any write, then archive exactly one
unverified `GrantEvidenceCandidate` linked to the immutable evidence version, source record and
source configuration. Never infer or change legal state.

## Explicit Non-Closure

No endpoint/UI/schema/source publication/source review/role binding/legal-state dispatch and no
adjacent service rule or second dataset. Do not duplicate the accepted resolver, seed a source,
absorb another V8 row, or treat candidate availability as grant evidence approval.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01`
- `FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01`
- `FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01`
- `FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01`

### External, gate and inherited prerequisites

- `gate` — `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.

- Approved source dependency cell: accepted Scheme A gate; accepted source carrier schema,
  resolver service and configuration API; evidence-version service; successor lane activation.

### Shared ownership serialization

- `backend/app/modules/documents/grant_evidence_ingestion_service.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- `FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01`

## Frozen Public Interface and Lineage Bytes

Create exactly `backend/app/modules/documents/grant_evidence_ingestion_service.py`. It exposes
these frozen, slotted, keyword-only DTOs and one synchronous callable:

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
    original_reference: str
    acquired_at: datetime
    acquisition_reason: str
    proposed_by: str
    proposed_at: datetime
    as_of: datetime
    facts: tuple[GrantEvidenceFact, ...]
    conflicts: tuple[GrantEvidenceConflict, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class IngestGrantEvidenceCandidateResult:
    candidate_id: str
    evidence_version_id: str
    source_config_id: str
    source_record_id: str
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

Raw strings and lookalike enums are rejected. IDs, reference/reason/fact names and values are
non-blank and bounded by their carrier columns; datetimes are UTC-naive. Fact names are unique.
Conflict names are unique, must also exist in facts, and each conflict contains at least two
distinct non-blank raw values. Facts must already be sorted by `(name, raw_value)`, conflicts by
`name`, and each conflict's raw values lexically; the service rejects rather than silently
reorders caller input.

The command consumes one already persisted immutable `DocumentEvidenceVersion`; this service does
not call `register_evidence_version` and never creates or mutates an evidence version. The version
must be current for its lineage, belong to the exact case/document, have `role=RAW_ATTACHMENT`,
`state=FINAL`, `review_state=PENDING`, no reviewer/final submission, and point to an existing
attachment belonging to the same document. Its stored `content_hash` remains the official raw-file
content identity.

Call `resolve_grant_evidence_source(ResolveGrantEvidenceSourceCommand(evidence_scope, as_of))`
before any candidate write. The resolved result supplies the exact source-config ID and snapshot
hash, source-record ID, source version and snapshot hash, and acquisition method; no caller value
may replace them.

Canonical JSON uses UTF-8, `ensure_ascii=False`, `sort_keys=True`, separators `(",", ":")`, and
`allow_nan=False`; hashes are lowercase SHA-256 of the exact stored text. Every datetime is
serialized as UTC-naive `value.isoformat(timespec="microseconds")`; `evidence_scope` is serialized
as its exact enum `.value`. No implicit `default=str`, timezone conversion or precision trimming
is permitted.

- `acquisition_snapshot` has exactly: `schema_version` =
  `CNIPA_GRANT_EVIDENCE_ACQUISITION_V1`, `case_id`, `document_id`, `attachment_id`,
  `evidence_version_id`, `evidence_content_hash`, `evidence_scope`, `source_config_id`,
  `config_snapshot_hash`, `source_record_id`, `source_version`, `source_snapshot_hash`, `original_reference`,
  `acquisition_method`, `acquired_at`, `acquisition_reason`, `proposed_by`, `proposed_at`, `as_of`.
- `candidate_snapshot` has exactly: `schema_version` =
  `CNIPA_GRANT_EVIDENCE_CANDIDATE_V1`, `evidence_scope`, `facts` (ordered objects with exact keys
  `name`, `raw_value`) and `conflicts` (ordered objects with exact keys `name`, `raw_values`).
- `conflict_snapshot` is `NULL` when conflicts is empty; otherwise it is the canonical JSON text
  of exactly the candidate snapshot's `conflicts` array. It is preserved evidence, never a
  selected/normalized legal status.

The database unique `evidence_version_id` is the replay identity. Existing candidate replay returns
`REUSED` only when every persisted foreign key, copied source/version/reference/method/time,
proposer/time, both canonical texts/hashes and conflict text match the newly derived exact bytes.
Any mismatch, duplicate/ambiguous row or corrupted hash is
`GRANT_EVIDENCE_CANDIDATE_CONFLICT`/409 with no write. Creation returns `CREATED`, sets
`review_status=PENDING` with no reviewer, and performs one flush but no commit/rollback.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01.md`
- `backend/app/modules/documents/grant_evidence_ingestion_service.py`
- `backend/tests/test_v8_grant_evidence_ingestion_service.py`
- `artifacts/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Require the exact persisted gate and lane activation; absent/revoked/future/scope-mismatched decisions are 409/no write.
- Call `resolve_grant_evidence_source` with the exact evidence scope and one captured naive `as_of`
  before creating or mutating any `Document`, `DocAttachment`, `DocumentEvidenceVersion` or
  `GrantEvidenceCandidate`. Missing, future, expired, revoked, rejected, unreviewed, inactive,
  scope/version/hash-mismatched or ambiguous source/configuration is the accepted `409` and zero
  write.
- Persist the accepted `GrantEvidenceCandidate` carrier with exact case/document/existing
  evidence-version,
  resolved source-record/configuration IDs, immutable source/acquisition/candidate snapshots and
  hashes, actual authenticated proposer, `PENDING` review and no reviewer. Caller owns the
  transaction; replay is exact and cannot create a second candidate for one evidence version.
- Archive extracted conflicts in the candidate snapshot/conflict field without selecting a legal
  status. No candidate, attachment, review state or source activation changes `Case.status`, emits
  a lifecycle event or confirms grant.

## Frozen RED / GREEN Matrix

1. A valid reviewed/active/effective source and exact GLOBAL configuration produce one PENDING
   candidate linked to the immutable evidence version and resolved source/config IDs.
2. Announcement and register scopes remain independent; cross-scope source/configuration fails.
3. Missing/revoked/future/expired/unreviewed/inactive/hash/version/ambiguous resolver outcomes are
   propagated as 409 before any business write.
4. Cross-case document/evidence, non-current/unreviewed or non-RAW_ATTACHMENT/non-FINAL evidence,
   malformed/unsorted fact-conflict input, malformed canonical snapshots,
   synthetic/default proposer and duplicate evidence-version candidate fail closed.
5. Same-command replay by the unique existing evidence-version ID returns the same candidate only
   when all immutable inputs/derived bytes/hashes match;
   changed replay and concurrent duplicate attempts return 409 without residue.
6. Caller rollback removes the candidate only; a fault after resolver/read validation and before or
   after candidate flush leaves no committed candidate and never changes the pre-existing evidence
   version; service never commits or rolls back.
7. No legal-state/lifecycle/fee/payment fact is created, including when candidate facts conflict.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_ingestion_service.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_ingestion_service.py`
- `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_source_carrier_schema.py tests/test_v8_grant_evidence_source_carrier_service.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/grant_evidence_ingestion_service.py tests/test_v8_grant_evidence_ingestion_service.py && .venv/bin/ruff format app/modules/documents/grant_evidence_ingestion_service.py tests/test_v8_grant_evidence_ingestion_service.py && .venv/bin/ruff check app/modules/documents/grant_evidence_ingestion_service.py tests/test_v8_grant_evidence_ingestion_service.py`
- `git diff --check -- backend/app/modules/documents/grant_evidence_ingestion_service.py backend/tests/test_v8_grant_evidence_ingestion_service.py tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted service/test change consumes the accepted
resolver and candidate carrier, makes the exact GREEN and targeted source-carrier regressions
pass, and proves zero legal-state effect; task-scoped lint/scope, serialized SQLite, dirty-baseline
and evidence checks pass; one independent reviewer approves the current contract/implementation;
atomic evidence and task gates pass. Only then may this task be reported PASS.
