# Contract — V8 Format Letter IN-Source Archive Vertical Successor

- Risk: `PROTECTED`
- Superseded closure: frontend-only execution of
  `FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01` (ordinal `92`).
- Outcome: expose one authenticated, idempotent HTTP command that composes the accepted
  Row89 context, Row90 render and Row91 archive services, then expose its Chinese action
  only for an IN-source panel and display the actual archived evidence version and hash.
- Reason for successor: Row91 has no production caller or HTTP endpoint; existing handoff
  responses contain no evidence version/hash; and the legacy handoff producer stores
  provenance values incompatible with Row89. A two-file UI implementation would therefore
  be mock-only and fail the observable product contract.

## Exact HTTP contract

Add:

```text
POST /official-documents/{source_document_id}/format-letter-archive
Permission: OfficialWorkflow.Update
Status: 201 for both first success and exact replay
```

Request:

```json
{
  "operation_id": "UUID",
  "selected_contact_id": "UUID or null",
  "remark": "string or null"
}
```

`operation_id` is required and is the deterministic handoff/idempotency identity. The
optional contact is an explicit Row89 override; null delegates to Row89 primary/default
selection. Remark is stripped to null and limited to 2000 characters. Actor always comes
from the authenticated current user. Invalid UUID/body remains FastAPI 422; no actor,
contact, case or operation identity is inferred.

Response:

```json
{
  "handoff": "LetterHandoffOut",
  "evidence_version_id": "UUID",
  "version_number": 1,
  "content_hash": "sha256:<64 lowercase hex>",
  "generated_document_id": "UUID",
  "attachment_id": "UUID",
  "file_name": "...docx",
  "role": "CLIENT_LETTER_WORD",
  "state": "DRAFT",
  "review_state": "PENDING",
  "is_current": true,
  "reused": false
}
```

Never expose the managed local path, inode or temporary compensation state. Preserve
Row89/90/91 business error status, code and details. Operation/provenance/partial-state
drift is `FORMAT_LETTER_ARCHIVE_CONFLICT` (409). A database commit failure is
`FORMAT_LETTER_ARCHIVE_PERSIST_FAILED` (500); compensation failure preserves
`FORMAT_LETTER_ARCHIVE_COMPENSATION_FAILED` (500).

## Exact service orchestration

Add one typed command/result/pending-operation seam in the official-workflow service. On a
new operation:

1. require a clean caller transaction and absence of any handoff or evidence lineage using
   the operation identity;
2. call `build_format_letter_context` with the named source and optional contact;
3. call `render_format_letter` with that immutable result;
4. create exactly one handoff with `id=operation_id`, the exact Row89
   mapping/template/contact/salutation provenance, the Row90 file name at
   `letters/{case_no}/{file_name}`, the normalized remark, and one required/included
   `FORMAT_LETTER_WORD` placeholder whose attachment is initially null;
5. call Row91 `archive_format_letter` exactly once with the authenticated actor;
6. return the Row91 pending managed-file identity plus the exact evidence/handoff response.

Do not call the legacy `prepare_letter_handoff` path and do not translate its incompatible
`CLIENT_PRIMARY_CONTACT`, `PRIMARY_CONTACT_TITLE` or `UNCONFIRMED` provenance. Do not
calculate a deadline, amount, eligibility, evidence identity or template choice in the API
or frontend.

For an existing `operation_id`, do not rebuild, rerender, create a file or register another
version. Load and validate one exact committed handoff, placeholder attachment, generated
document/attachment and `format-letter:{operation_id}` evidence version. The request source,
selected contact, normalized remark, stored provenance, role/state/review/current identity,
file name/path, attachment and content hashes must agree. Exact replay returns the stored
result with `reused=true`; missing, partial, ambiguous, superseded or divergent state is
409. Reusing the operation ID for another source/contact/remark is 409.

The service never commits or rolls back. The API rolls back any pre-pending exception. On
successful preparation it commits once. If commit fails it rolls back, removes only the
Row91-created file using the exact device/inode identity under the Row91 lock, and raises
the persist error; if compensation detects identity drift its stronger compensation error
wins. No file is deleted after a committed response or exact replay.

## Exact frontend behavior

Add the typed client command/result. `LetterHandoffPanel` accepts the document direction;
the new `生成并归档格式函` action is rendered only for normalized `IN`. Preview success and
backend response remain authoritative; the frontend does not infer latest evidence,
deadline, fee or legal eligibility. It retains one `crypto.randomUUID()` operation ID
across retries for the same source until success, resets it when the source changes, and
sends the current remark with no fabricated contact identity.

After success, disable the action and display `证据版本 v{version_number}` plus the exact
full `content_hash`. Never label an attachment ID, document ID or file path as a version or
hash. Existing legacy handoff preview/status behavior may remain visible for OUT documents,
but the new archive action and archive-result presentation must not appear there.

`DocumentDetail.vue` mounts/passes the panel for IN as well as existing supported behavior
and passes the actual direction. `DocumentDispatch.vue` passes the selected document's
direction so arbitrary OUT selections cannot expose the new action.

## Exact implementation allowlist

- `backend/app/modules/official_workflows/service.py`
- `backend/app/modules/official_workflows/api.py`
- `backend/app/modules/official_workflows/schemas.py`
- `backend/tests/test_v8_format_letter_archive_api.py`
- `frontend/src/api/officialWorkflows.ts`
- `frontend/src/api/officialWorkflows.types.ts`
- `frontend/src/modules/officialWorkflows/components/LetterHandoffPanel.vue`
- `frontend/src/modules/documents/pages/DocumentDetail.vue`
- `frontend/src/modules/documents/pages/DocumentDispatch.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-format-letter-in-source-ui.spec.ts`

## Verification and non-goals

Backend RED/GREEN covers 201 new success, exact replay/no new write, operation drift,
partial state, OUT/stale/unreviewed rejection, permission/actor injection, exact response,
commit rollback/file compensation and Row89/90/91 propagation. Run the Row89, Row90, Row91
and existing handoff API regressions in the serialized SQLite lane.

Targeted Playwright covers IN visibility, exact Chinese action, one stable operation ID on
retry, POST payload/path, success version/hash rendering and OUT non-visibility. Run
exact-file ESLint, scoped frontend type checking, scoped Ruff/format/diff and independent
High review of the exact vertical commit.

No email send, evidence approval/finalization, download endpoint, background job, bulk
generation, alternate template/contact policy, legacy handoff migration, schema/migration,
second page capability or adjacent cleanup is included.
