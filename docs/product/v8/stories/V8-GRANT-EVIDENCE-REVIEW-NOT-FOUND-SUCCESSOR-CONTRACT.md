# Story V8-GRANT-EVIDENCE-REVIEW-NOT-FOUND-SUCCESSOR-CONTRACT

- Risk: `PROTECTED`.
- Outcome: make the accepted grant-evidence review service expose the API task's required
  not-found result without adding an API-side product lookup.
- Successor to: `FPMS-V8-GRANT-EVIDENCE-REVIEW-SERVICE-20260712-01` and
  `FPMS-V8-GRANT-EVIDENCE-REVIEW-API-20260712-01`.
- Authority: the row-208 `TC-API` frozen 404 acceptance semantic and the independent High P1
  finding against commit `9da9f082ace6b471c87581269d92be2a498a3cf9`.

## Exact correction

When the exact candidate ID does not exist, the service raises
`GRANT_EVIDENCE_REVIEW_NOT_FOUND` with HTTP status 404 before authority resolution or mutation.
The API delegates once to that service and preserves its error envelope. This exact rule
supersedes only the earlier service acceptance-matrix statement that grouped a missing candidate
with corrupt, noncanonical, cross-bound or inconsistent candidate state under 409.

All malformed input remains 400. An existing candidate with invalid authority, role separation,
source lineage, canonical bytes, terminal replay, compare-and-swap or dispatch state remains
409/no write. No caller transaction is committed by the service.

## Exact paths and verification

- `backend/app/modules/documents/grant_evidence_review_service.py`
- `backend/tests/test_v8_grant_evidence_review_service.py`
- `backend/tests/test_v8_grant_evidence_review_api.py`
- `docs/product/v8/stories/V8-GRANT-EVIDENCE-REVIEW-NOT-FOUND-SUCCESSOR-CONTRACT.md`

Targeted RED proves the real service and HTTP route return the obsolete 409. GREEN requires both
to return the same typed 404 envelope, followed by the complete focused service/API suites,
scoped Ruff, exact diff inspection and independent High review.

## Non-goals and rollback

No API-side candidate lookup, route/schema/permission change, source or role policy change,
accepted dispatch change, status/deadline/fee/document mutation, schema/migration, adjacent
cleanup or broad regression. Rollback reverts only this typed missing-candidate distinction and
its targeted tests/story card.
