# Story V8-DOCUMENT-ATTACHMENT-EVIDENCE-REVIEW-VERTICAL-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Base: `ed86cadc74e48a1fab4d156360dbacb1bdc9780e`
- Outcome: register generated document attachments as current evidence with exact
  template lineage and server-owned creator identity, expose the existing review
  transition and current evidence projection through the document API and frontend, and
  let authorized non-creators approve or reject a pending attachment from the attachment
  list.
- Authority: frozen catalog rows 49–54, their exact task contracts and preserved
  historical RED/GREEN evidence; `docs/product/v8/domain-contract.md`; and the current
  D4 actor, role and registration contracts.
- Change mode: row 49 current-tree verification, followed by exact archive-hunk adoption
  in the serialized order `49→50→51` and `50→52→53→54`.

## Catalog IDs and dependencies

1. `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01` (ordinal `49`)
2. `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01` (ordinal `50`)
3. `FPMS-V8-DE-REVIEW-API-20260712-01` (ordinal `51`)
4. `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01` (ordinal `52`)
5. `FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01` (ordinal `53`)
6. `FPMS-V8-DE-REVIEW-UI-20260712-01` (ordinal `54`)

Row 49 is already current on the base. Row 50 also depends on the current D4-06 evidence
role extension and D4-07 evidence registration matrix; row 51 depends on the current
review service. The shared document service, API, schemas and frontend files remain under
one serialized story owner.

## Exact product and test paths

- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/evidence_review_schemas.py`
- `backend/tests/test_v8_attachment_evidence_atomic_adapter.py`
- `backend/tests/test_v8_generated_attachment_evidence_adapter.py`
- `backend/tests/test_v8_document_evidence_review_api.py`
- `backend/tests/test_v8_attachment_evidence_read_projection.py`
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/api/contracts/v8_document_evidence_review.contract.ts`
- `frontend/src/modules/documents/components/AttachmentList.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-document-evidence-review-ui.spec.ts`
- `docs/product/v8/stories/V8-DOCUMENT-ATTACHMENT-EVIDENCE-REVIEW-VERTICAL-CURRENT-ADOPTION.md`

No old task, taskctl, evidence, ledger, review, manifest or shared-ownership file enters
the story.

## Observable contracts

- User uploads keep the current atomic file/attachment/evidence behavior and server-owned
  creator identity already established by row 49.
- Wizard-generated attachments register exactly one `GENERATED_ATTACHMENT` evidence
  version in `DRAFT/PENDING`, with creator identity from the authenticated user and
  lineage
  `generated:<template-id>:<first16 sha256(template-code)>:<attachment-id>`. Direct
  `commit=True` and wizard `commit=False` transaction and file-compensation behavior stay
  distinct.
- `POST /documents/evidence-versions/{evidence_version_id}/review` requires `Doc.Edit`,
  takes the evidence identity only from the path, takes the reviewer only from the
  authenticated user, delegates to the current review service, and commits success or
  replay while rolling back every service error.
- The bodyless document detail read exposes only persisted current evidence facts per
  attachment: evidence version, role, creator, reviewer, review state, current and final.
  It infers no readiness or lifecycle state and fails closed on malformed current data.
- The frontend adapter preserves those exact facts and returns the freshly read
  projection after review. The attachment list shows creator, reviewer and review state;
  an authorized non-creator can approve or reject pending evidence, while self-review and
  mapped failures remain explicit in Simplified Chinese.
- Current D4 actor ownership, evidence roles, registration validation, permissions and
  all later document successors remain unchanged.

## Verification and preserved history

Historical RED/GREEN is preserved by reference and is not rerun. Fresh verification is
limited to the exact row 49–54 backend tests, the isolated frontend contract, the focused
Playwright story, scoped Ruff/format/type/lint checks and exact diff checks. SQLite-writing
backend checks are serialized with other repository work.

The row 49 focused test and attachment-registration service seam are byte-unchanged from
archive ref `6b2ef89da447353380b99853168d4d38aaf9210a`; its upload decorator has only the
documented row 52 response-shape guard. Rows 50–54 adopt only their exact product and test
hunks from that archive; current successor bytes win wherever the archive contains later
unrelated work. The row 50 test differs from its archive blob by one neutral
`fee_reduction: "0"` case-creation field required by the current case-create successor;
the document behavior under test is unchanged.

Fresh story-branch verification:

- The first serialized four-file backend tranche produced `88 passed, 4 failed`. One
  row 49 failure proved the shared response schema leaked row 52 defaults into upload;
  three row 50 setup failures proved the current case-create successor now requires an
  explicit fee-reduction choice.
- The two single-cause successor checks then produced `1 passed` and `3 passed`.
  Re-running the exact four-file tranche produced `92 passed`; its three warnings are
  inherited `passlib` and Pydantic deprecations.
- The isolated row 53 TypeScript contract and exact-file ESLint pass.
- Full frontend typecheck reproduces only the seven inherited integration-base errors in
  `billing.ts`, `http.ts`, `officialWorkflows.ts` and `CaseFeesTab.vue`; no owned document
  path reports an error.
- The exact row 54 Playwright file produces `3 passed` against the isolated mocked UI.
- Scoped Ruff and exact diff-check pass. Ruff format-check reports seven exact backend
  files already formatted and the shared `documents/api.py` archive-style layout; the
  latter already had two formatter differences on the clean base and is not broadly
  reformatted.

## Non-goals, minimal successor alignment and rollback

This story does not change evidence registration or review-service rules, lifecycle or
legal status, official-fee or payment behavior, document templates, migrations, source
activation, customer decisions, unrelated attachment metadata, router structure, or any
later lifecycle adapter. Fresh targeted checks required exactly two minimal successor
alignments: the upload route excludes only row 52's seven new default projection fields
so row 49's response body remains exact, while document detail still returns them; and
the row 50 fixture supplies the current case-create contract's neutral explicit fee
reduction. No other successor alignment is included.

Rollback reverts the single story commit, restoring the pre-story document adapters and
UI while leaving row 49, D4 role/registration contracts, the review service and all later
successors intact.
