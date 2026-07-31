# Story V8-LIFECYCLE-EVIDENCE-API-ADAPTERS-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: adopt and prove the ten frozen document-evidence API adapters for the
  preliminary, rectification, publication, substantive, reexamination and terminal
  application lifecycle outcomes.
- Change mode: exact current adoption of accepted archive slices for ordinals 78–83,
  followed by test-first implementation of the missing ordinals 84–87.
- Authority: `docs/product/v8/domain-contract.md`, the frozen catalog contracts and the
  accepted lifecycle/evidence-review predecessors.
- Archive comparison anchor:
  `6b2ef89da447353380b99853168d4d38aaf9210a`.

## Catalog IDs and ownership order

1. `FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01` (ordinal 78)
2. `FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01` (ordinal 79)
3. `FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01` (ordinal 80)
4. `FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01` (ordinal 81)
5. `FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01` (ordinal 82)
6. `FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01` (ordinal 83)
7. `FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01` (ordinal 84)
8. `FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01` (ordinal 85)
9. `FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01` (ordinal 86)
10. `FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01` (ordinal 87)

Ordinal 77 certificate-archived activity is not part of this story.

## API and evidence boundaries

Each endpoint is a single `POST /documents/{document_id}/lifecycle/...` route protected by
`Doc.Edit`. The authenticated user supplies the actor identity; the client cannot supply
case, event, reviewer, source-activity, superseded-event or confirmation state. The route
owns commit on success and rollback on every exception.

Every adapter consumes only a current, final, independently approved
`OFFICIAL_FINAL_PDF` evidence version with canonical lineage, hash and naïve review time.
The endpoint document determines the case. Missing objects preserve 404, relationship
mismatches preserve 400, stored-evidence conflicts preserve 409, authentication and
permission remain 401/403, and strict request failures remain 422.

The preliminary, pass, publication, substantive and reexamination adapters emit one fixed
evidence kind and empty lifecycle payload. Rectification additionally consumes the exact
confirmed official deadline snapshot already stored on its document.

Application rejection allows only `REJECTION_DECISION` or
`REEXAMINATION_FINAL_REJECTION_DECISION`. Application abandonment allows only
`DEEMED_ABANDONMENT_NOTICE` or `RIGHT_ABANDONMENT_CONFIRMATION`. Application withdrawal
requires two distinct reviewed evidence versions in fixed order: the request belongs to
the endpoint document, while the official confirmation belongs to the same case.
Application restoration requires the official restoration decision and one explicit
restored procedure stage from the nine stages accepted by its lifecycle rule.

No adapter duplicates lifecycle rule decisions or writes case status directly. All ten
invoke only their named accepted lifecycle event through the existing lifecycle service.

## Exact paths

- `backend/app/modules/documents/lifecycle_evidence_adapters.py`
- `backend/app/modules/documents/api.py`
- the ten matching `backend/tests/test_v8_*_evidence_api.py` focused files

The six ordinal 78–83 test files are byte-identical to the archive anchor. The adapter
module adopts only their required archive slices; acceptance-notice and OA-notice archive
functions are intentionally excluded. The current API adopts only the six required route
hunks so later evidence-review/read successors remain intact.

## Current verification

Before terminal implementation, the exact four ordinal 84–87 tests produced `15 failed`;
the failures proved the four route surfaces were absent (router count zero / HTTP 404).

The final controller-authorized serialized tranche contained the ten focused adapter tests
plus `test_addgap_document_deadline_carrier.py`: `308 passed`, with only three inherited
third-party/Pydantic deprecation warnings. Scoped Ruff check and exact diff-check pass.

An independent High reviewer must review the exact candidate/range, verify the six archive
test blob identities, rerun the decisive tranche once and confirm the product/test
fingerprint and non-goals.

## Non-goals and rollback

No certificate-archived adapter, acceptance/OA adapter restoration, generic lifecycle
endpoint, business-rule duplication, document creation, direct status write, frontend,
schema/migration, customer/source decision, ledger/disposition/review edit, governance
artifact or milestone claim. Rollback reverts the two product files, ten focused tests and
this story card as one candidate while retaining the accepted lifecycle and evidence
predecessors.
