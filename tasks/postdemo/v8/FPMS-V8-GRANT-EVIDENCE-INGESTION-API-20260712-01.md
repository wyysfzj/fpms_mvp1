# FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01

Status: CONTRACT RE-FROZEN / READY FOR IMPLEMENTATION
Risk class: `PROTECTED`
Runbook: `P0-shared-router-story`
Catalog ordinal: `201`

## Authority and prerequisites

- Scheme A customer source SHA-256
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Accepted ingestion service story
  `V8-GRANT-EVIDENCE-INGESTION-SERVICE-CURRENT-ADOPTION` at implementation tip
  `cada0a256b2170eab934b5a3a55711880abd1466`.
- Accepted official-copy verification and institution role/source carriers remain authoritative.

The former API task predated the accepted terminal official-copy chain and allowed no exact route,
actor/time injection or payload contract. This successor is only the transport adapter for the
accepted ingestion service; it must not query or reproduce product rules.

## Exact closure

Create `backend/app/modules/documents/grant_evidence_schemas.py` with strict Pydantic v2 models:

```python
class GrantEvidenceFactIn(BaseModel):
    name: str
    raw_value: str


class GrantEvidenceConflictIn(BaseModel):
    name: str
    raw_values: tuple[str, ...]


class GrantEvidenceCandidateIn(BaseModel):
    case_id: UUID
    evidence_version_id: UUID
    evidence_scope: GrantEvidenceScope
    expected_terminal_event_id: UUID
    facts: tuple[GrantEvidenceFactIn, ...]
    conflicts: tuple[GrantEvidenceConflictIn, ...] = ()


class GrantEvidenceCandidateOut(BaseModel):
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
    disposition: str
```

Every input model uses `ConfigDict(extra="forbid")`. Strings must be nonblank, trimmed, NUL-free
and at most 4096 characters. Facts are nonempty, unique by name and already sorted by
`(name, raw_value)`. Conflicts are unique and sorted by name; every conflict name exists in facts;
each `raw_values` tuple has at least two distinct values already sorted lexically. Reject rather
than reorder. UUID fields use Pydantic UUID validation and are passed to the service in canonical
string form. Output is validated from the exact service result.

Add exactly one route:

```text
POST /documents/{document_id}/grant-evidence-candidates
permission: Doc.Edit
success: 201 CREATED, 200 REUSED
```

The path `document_id` is a UUID and is the sole document identity. The body supplies case,
evidence-version, exact terminal-event, scope and raw fact/conflict input. The route injects the
authenticated actual user's ID as `proposed_by` and exactly one server UTC-naive timestamp as
`proposed_at`; actor or time are never accepted from the client. It constructs one exact
`IngestGrantEvidenceCandidateCommand`, delegates once to `ingest_grant_evidence_candidate`, and
performs no direct product-table read/write or business-rule validation.

The route owns commit/rollback. `CREATED` maps to 201 and `REUSED` to 200. Preserve framework
401/403/422 and service 400/409 semantics. Any service or commit exception rolls back and is
re-raised unchanged. No response envelope is added beyond the exact response model.

## Non-closure

No second endpoint, GET/list/read/review route, router rewiring, service/schema/migration change,
source/role/default publication, official-copy event creation, candidate review, legal-state
dispatch, lifecycle/deadline, document/evidence mutation, fee/payment behavior, frontend or UI.
Creating or replaying a PENDING candidate never confirms grant.

## Allowed files

- this task file;
- `backend/app/modules/documents/grant_evidence_schemas.py`;
- `backend/app/modules/documents/api.py`;
- `backend/tests/test_v8_grant_evidence_ingestion_api.py`.

## Frozen acceptance matrix

1. Exact strict schema/route/permission contract is present once and rejects extra actor/time or
   malformed/unsorted/duplicate facts and conflicts with 422 before delegation.
2. The route injects path document UUID, authenticated user and one server UTC-naive timestamp,
   passes all remaining body fields exactly, delegates once and never queries product tables.
3. CREATED/REUSED return exact response bodies with 201/200; commit occurs once only after service
   success.
4. Permission/validation failures do not delegate or open product writes; service 400/409 and
   commit failures roll back without translation.
5. No legal/lifecycle/document/evidence/deadline/fee/payment side effect or second route exists.

## Verification

- Focused RED/GREEN pytest: `backend/tests/test_v8_grant_evidence_ingestion_api.py`.
- Shared document-router and accepted ingestion-service regressions.
- Scoped Ruff/format and exact three-path implementation diff-check.
- One independent High reviewer reviews the exact implementation range and reruns decisive checks.
- PASS requires `P0/P1/P2 = 0/0/0`; no Full or release gate belongs here.
