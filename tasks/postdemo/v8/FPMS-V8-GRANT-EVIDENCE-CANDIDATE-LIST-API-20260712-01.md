# FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01

Status: CONTRACT RE-FROZEN / READY FOR IMPLEMENTATION
Risk class: `PROTECTED`
Runbook: `P0-shared-router-story`
Catalog ordinal: `203`

## Authority and prerequisites

- Scheme A SHA-256
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Accepted candidate-read service implementation `72126838a8032863bc445a5dcb2612fbb6e42815`.
- Accepted ingestion API owns the existing POST on the same resource collection.

## Exact closure

Extend `grant_evidence_schemas.py` with output-only strict projection models matching every field of
`GrantEvidenceCandidateRead`, including nested exact fact/conflict models, source/version,
terminal/proposal-role identities, proposer/reviewer/review data, hashes and raw conflicts. Output
models accept attributes and do not normalize, infer or choose a conflict value.

Add exactly one bodyless route:

```text
GET /documents/{document_id}/grant-evidence-candidates
permission: Doc.Read
response: 200 list[GrantEvidenceCandidateReadOut]
```

The path is a UUID. The route injects exactly one server UTC-naive `read_at`, constructs one exact
`ListGrantEvidenceCandidatesCommand`, delegates once to `list_grant_evidence_candidates`, and
validates the exact ordered tuple into the response list. It performs no direct product query,
flush, commit or rollback. Preserve 401/403/404/409/422 semantics. The GET has no body, query
parameters or alternate route; an existing document with no candidates returns `[]`.

## Non-closure

No POST/review endpoint change, service/schema/migration, current-source resolution, legal-state
inference/dispatch, document/evidence mutation, lifecycle/deadline, fee/payment or frontend/UI.

## Allowed files

- this task file;
- `backend/app/modules/documents/grant_evidence_schemas.py`;
- `backend/app/modules/documents/api.py`;
- `backend/tests/test_v8_grant_evidence_candidate_list_api.py`.

## Frozen acceptance matrix

1. Exact GET exists once with `Doc.Read`, UUID path, no body/query and exact response model.
2. Path plus one server time maps to one service command; no direct query/write/transaction close.
3. Empty and ordered multiple projections return exact 200 JSON preserving raw conflicts/reviews.
4. Auth/permission/path/service 401/403/422/404/409 semantics remain unchanged and no second route
   or product side effect is introduced.

## Verification

- Focused RED/GREEN candidate-list API pytest.
- Ingestion POST, candidate-read service and shared document-router regressions.
- Scoped Ruff and exact three-path diff-check; do not format unrelated shared-router bytes.
- Independent High review; PASS requires P0/P1/P2 `0/0/0`.
