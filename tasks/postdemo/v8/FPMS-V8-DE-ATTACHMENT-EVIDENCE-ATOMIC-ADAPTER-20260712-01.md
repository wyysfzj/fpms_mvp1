# FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `49`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`
- Delta-3 supplemental materialization row: `13`
- Source catalog line: `435`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: Exact adapter test proves the old direct write/missing activity/premature state.
- GREEN expectation: Exact adapter test plus listed inherited regressions pass; only the named entrypoint changes.

## Exact Closure Slice

Existing attachment POST records the authenticated creator and registers one evidence version in the same transaction; file/attachment/version all succeed or roll back together.

## High Contract Audit — 2026-07-14

Execution stopped before RED and before any product/test edit because the approved
design does not uniquely determine the inputs required by the accepted
`register_evidence_version()` dependency. This is a contract ambiguity, not an
implementation failure.

### Frozen facts

- The existing multipart endpoint accepts only `file`, optional
  `official_file_role`, and optional `source_role_alias`; it returns the existing
  `DocAttachmentOut` envelope with status 201.
- The existing attachment catalog has 18 roles and also permits an attachment
  with no official role. The accepted V8 evidence contract has nine different
  `EvidenceRole` values. Only `FILING_FULL_WORD` is an exact shared machine value.
- Registering a version additionally requires a non-blank `lineage_key`, an exact
  `EvidenceVersionState` (`DRAFT` or `FINAL`), authenticated `creator_id`, and the
  content hash. Neither the endpoint nor the adapter row freezes the source of
  `lineage_key` or state.
- The accepted register-version service is caller-transaction owned and does not
  commit. The existing upload service writes the managed file before creating the
  attachment and then commits internally; it removes the file only when the file
  write itself fails. A later registration/flush/commit failure therefore needs an
  explicitly owned compensation boundary.

### Credible interpretations that cannot be selected by High

1. Add explicit multipart fields for evidence role, lineage and state, rejecting
   missing values while preserving the existing attachment role separately.
2. Derive evidence role, lineage and state from the 18-role attachment catalog,
   which requires a complete mapping and stable lineage policy not present in the
   design.
3. Register versions only for a mapped subset and retain legacy-only attachments
   for the rest, which conflicts with the unqualified phrase "registers one
   evidence version" unless explicitly authorized.

The filesystem compensation owner is likewise ambiguous: the service can own the
whole upload/register/commit unit, the API can commit and compensate using an
explicit service result, or a transaction hook can manage the file lifecycle.
Those choices have different public/service contracts and failure behavior.

### Required Ultra re-freeze

Before resuming RED, freeze all of the following in this task without enlarging
the closure slice:

1. Exact multipart request fields, validation/error codes, and whether the 201
   `DocAttachmentOut` response remains unchanged or exposes evidence identity.
2. Complete behavior for every accepted attachment role and for a missing role:
   exact `EvidenceRole`, `EvidenceVersionState`, `lineage_key`, or an explicit
   rejection/legacy-only rule.
3. Exact lineage identity rule for repeated uploads and distinct documents.
4. Authenticated creator propagation via `current_user_dep`, while preserving
   `Doc.Attach` parameter-injected permission enforcement.
5. Caller-owned database transaction boundary, flush/commit location, and managed
   file compensation owner/order for file-write, attachment-flush,
   version/activity-flush, and commit failures.
6. Retry/idempotency semantics for repeated HTTP uploads and the exact observable
   result after every rollback path.

No RED test or product change is authorized until this re-freeze is complete.

## Ultra Contract Resolution — 2026-07-14

The approved delta-2 resolves every item in the preceding High audit without changing
this task's closure slice, HTTP wire or response model. Product implementation remains
NOT STARTED and must begin again from the task-owned RED only after both dependencies
pass.

### Frozen HTTP, actor and role mapping

- Preserve the sole existing multipart
  `POST /api/v1/documents/{document_id}/attachments`, parameter-injected `Doc.Attach`,
  request fields `file`, optional `official_file_role` and optional
  `source_role_alias`, status 201 and the existing direct `DocAttachmentOut` response.
  Do not add an evidence form field or expose evidence identity in the response.
- Add `current_user: T_User = current_user_dep`; the evidence-version creator and the
  DOCUMENT activity actor are both exactly `current_user.id`. `actor_id=None`, a request
  actor field and actor inference from attachment metadata are prohibited.
- Derive the legal evidence role only from the raw multipart `official_file_role` value,
  before `_resolve_attachment_manifest_metadata()` performs legacy normalization. The
  evidence-role decision and persisted legacy display metadata are independent:

| Raw multipart input | Frozen evidence role |
| --- | --- |
| `official_file_role` exactly `FILING_FULL_WORD` | `EvidenceRole.FILING_FULL_WORD` |
| Any of the other 17 accepted official-file roles | `EvidenceRole.RAW_ATTACHMENT` |
| Missing or blank `official_file_role` | `EvidenceRole.RAW_ATTACHMENT` |
| Alias-only upload, including `source_role_alias="完整递交文件"` | `EvidenceRole.RAW_ATTACHMENT` |

  Alias-only `完整递交文件` remains `RAW_ATTACHMENT` even when the legacy resolver stores
  `DocAttachment.official_file_role=FILING_FULL_WORD`. Case/whitespace normalization,
  aliases, stored attachment metadata and content hash must never promote a raw request
  to a formal evidence role.
- Every successful POST registers one `DRAFT` / `PENDING` evidence version with
  `lineage_key=f"attachment:{attachment.id}"` and version `1`. A repeated POST, including
  the same content hash, creates a distinct attachment, distinct lineage and independent
  version-1 fact; there is no HTTP idempotency, hash deduplication or replacement
  inference.

### Frozen service result and transaction ownership

The service returns this uncommitted result:

```python
@dataclass(frozen=True, slots=True)
class PendingAttachmentEvidenceUpload:
    attachment: DocAttachment
    evidence_version: EvidenceVersionResult
    managed_file_path: Path
```

- Before creating a managed file, the service validates the document, raw explicit role,
  file name, MIME and authenticated actor. A pre-file validation failure performs no
  filesystem cleanup.
- The service writes the managed file, adds the attachment, registers the version plus
  its DOCUMENT activity/evidence link, retains the compatible grant-notice
  `T_GrantFeeTask` ensure call, and flushes the complete database unit. It does not
  commit, rollback or refresh.
- The API is the sole outer transaction owner. It calls the service, commits exactly once
  after receiving `PendingAttachmentEvidenceUpload`, and rolls back any service or commit
  failure. Attachment, evidence version, DOCUMENT activity/link and any compatible
  `T_GrantFeeTask` write therefore share one database transaction.

### Frozen managed-file compensation

The database and filesystem are not XA. Cleanup ownership is split by whether the
service returned a pending result:

1. A file-write failure is service-owned. After successful cleanup, an existing
   `BusinessError` such as the size-limit 400 is re-raised unchanged; another storage
   exception becomes 500 `ATTACHMENT_STORAGE_WRITE_FAILED`.
2. After the file exists but before the pending result returns, any attachment,
   evidence-version, DOCUMENT activity/link, compatibility-carrier validation or flush
   failure is service-owned. The service deletes the file, preserves an existing
   `BusinessError`, and maps another exception to 500 `ATTACHMENT_PERSIST_FAILED`; it
   performs no commit or rollback. The API rolls back but does not attempt a second
   delete because it received no pending result.
3. After the API receives the pending result, commit failure is API-owned. The API first
   rolls back, then synchronously deletes `managed_file_path`, and returns 500
   `ATTACHMENT_PERSIST_FAILED`. The service must not delete this post-result path.
4. `FileNotFoundError` during any required cleanup is cleanup success and preserves the
   original business/storage/persistence outcome. Any other delete failure takes
   precedence and returns 500 `ATTACHMENT_STORAGE_COMPENSATION_FAILED`; server logs must
   retain the original exception and residual path.
5. No error response, code, message or details may expose an absolute path, residual
   relative path or original file name. Successful commit closes the compensation window
   and performs no delete. The service/API ownership split must prevent double deletion.

The remaining response matrix is unchanged: attachment/file/relationship business
validation is 400; unauthenticated/forbidden is 401/403; missing document is 404
`DOCUMENT_NOT_FOUND`; an inherited lifecycle projection conflict remains 409; missing
multipart `file` is 422.

### Task 75 and legal-effect boundary

- Do not delete or redefine `_advance_grant_notice_case_after_attachment()` in this task.
  `FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01` independently removes only the
  attachment-to-`Case.status=GRANTED` shortcut at documents-service order key `7`.
- The existing `T_GrantFeeTask` remains the compatible V8 section 6.3 downstream
  execution carrier; it is not a `FeeObligation`. Keep its existing ensure call inside
  this outer transaction.
- This adapter creates no fee obligation, fee draft, payment, formal-role promotion or
  new legal/lifecycle inference. Until task 75 passes, do not claim the generic
  attachment path is legal-status neutral.

### Delta-3 inherited RAW guard boundary

- This adapter keeps exactly one direct RAW-role prerequisite:
  `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`. Delta-3 makes that prerequisite
  directly depend on both the RAW registration guard and the external-submission
  positive-role guard, so this adapter inherits both guards transitively. Do not add
  either guard as a direct dependency or duplicate either service rule here.
- The inherited guard regressions are read-only expectations using the real
  `EvidenceRole.RAW_ATTACHMENT`: raw evidence registers only as `DRAFT/PENDING` and
  cannot fresh or replay external submission. This adapter still owns only attachment,
  evidence-version, activity/link, compatible-carrier and managed-file atomicity.

### Exact task-owned test matrix

All cases below belong to
`backend/tests/test_v8_attachment_evidence_atomic_adapter.py`; inherited metadata tests
remain read-only.

1. Exact raw `FILING_FULL_WORD` returns the unchanged 201 `DocAttachmentOut` and records
   `FILING_FULL_WORD`, `DRAFT/PENDING`, `attachment:{id}`, version 1, creator/activity
   actor `current_user.id`, and one DOCUMENT evidence link after one API commit.
2. Parameterize all other 17 accepted explicit roles and prove each records
   `RAW_ATTACHMENT` while preserving its existing attachment display metadata.
3. Missing/blank role and alias-only inputs record `RAW_ATTACHMENT`; specifically,
   `source_role_alias="完整递交文件"` may persist legacy `FILING_FULL_WORD` metadata but
   must remain raw evidence. A non-exact case/whitespace variant must not gain formal-role
   authority through normalization.
4. Two successful same-byte/same-hash POSTs return two attachment IDs and create two
   `attachment:{id}` lineages, each at version 1.
5. The service returns `PendingAttachmentEvidenceUpload`, flushes attachment/version/
   DOCUMENT activity/link and compatible `T_GrantFeeTask` writes, and never calls
   commit, rollback or refresh; it creates no obligation, draft or payment.
6. Validation before managed-file creation leaves no file and calls no cleanup; 400/404
   `BusinessError` values are preserved.
7. Size-limit `BusinessError` during write cleans the partial file and preserves its 400;
   an ordinary write exception cleans the partial file and returns
   `ATTACHMENT_STORAGE_WRITE_FAILED`.
8. A post-write/pre-return `BusinessError` cleans the file and is preserved; an ordinary
   attachment/version/activity/link validation or flush failure cleans the file and
   returns `ATTACHMENT_PERSIST_FAILED`. The API rolls back and does not double-delete.
9. API commit failure rolls back, deletes only the pending result's path and returns
   `ATTACHMENT_PERSIST_FAILED`; a successful commit performs no cleanup.
10. Parameterize service-write, service-pre-return and API-post-result cleanup with
    `FileNotFoundError`; each is treated as cleanup success and preserves the originating
    error.
11. Parameterize required cleanup failure at all three ownership points; each returns
    `ATTACHMENT_STORAGE_COMPENSATION_FAILED`, logs the original error plus residual path,
    and leaks no path or original filename in the response.
12. Auth/permission/missing-document/missing-file and inherited lifecycle conflict retain
    401/403/404/422/409 semantics, and the inherited metadata suite proves the multipart
    fields and 201 response remain compatible.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-REGISTER-VERSION-20260712-01`

### External, gate and inherited prerequisites

- `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`
- `transitive through the RAW-role prerequisite` —
  `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01` and
  `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`; neither is a direct
  dependency of this adapter.
- `inherited` — `backend/tests/test_document_attachment_upload_metadata_api.py`: Exact read-only pre-V8 regression required by the approved dependency alias.

- Approved source dependency cell (verbatim): register version; existing attachment tests

### Shared ownership serialization

- `backend/app/modules/documents/api.py` order key `1`; project this order only across owners present in the active manifest.
- `backend/app/modules/documents/schemas.py` order key `1`; project this order only across owners present in the active manifest.
- Preserve the complete `backend/app/modules/documents/service.py` owner order; do not
  project a shortened active-manifest chain:
  1. `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
  2. `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`
  3. `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
  4. `FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01`
  5. `FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01`
  6. `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
  7. `FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01`
  8. `FPMS-V8-CERTIFICATE-ARCHIVED-ACTIVITY-20260712-01`
  9. `FPMS-V8-OA-REPLY-DATE-RECEIPT-PROJECTION-20260712-01`

  This task owns key `1`; all nine product executions are serialized in this order.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01.md`
- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/schemas.py`
- `backend/tests/test_v8_attachment_evidence_atomic_adapter.py`
- `artifacts/FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- Dependency gates:
- `./scripts/task_validate.sh FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- `./scripts/task_validate.sh FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`
- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_attachment_evidence_atomic_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_attachment_evidence_atomic_adapter.py tests/test_document_attachment_upload_metadata_api.py`
- Read-only inherited RAW guard regressions, using real `EvidenceRole.RAW_ATTACHMENT` and
  serialized through `GLOBAL_SQLITE_SERIAL_QUEUE`:
  `cd backend && .venv/bin/pytest -q tests/test_v8_raw_attachment_registration_guard.py tests/test_v8_external_submission_role_allowlist.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/api.py app/modules/documents/service.py app/modules/documents/schemas.py tests/test_v8_attachment_evidence_atomic_adapter.py && .venv/bin/ruff format app/modules/documents/api.py app/modules/documents/service.py app/modules/documents/schemas.py tests/test_v8_attachment_evidence_atomic_adapter.py && .venv/bin/ruff check app/modules/documents/api.py app/modules/documents/service.py app/modules/documents/schemas.py tests/test_v8_attachment_evidence_atomic_adapter.py`
- `git diff --check -- backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_v8_attachment_evidence_atomic_adapter.py tasks/postdemo/v8/FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
- Evidence validation (single lane; no manifest or peer arguments): `python3 scripts/atomic_evidence_validate.py FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- If validation has post-init peer dirt, use that same wrapper with exactly one common
  authoritative execution `--manifest` containing this task and every peer, plus one
  `--concurrent-task <PEER-TASK-ID>` for every peer, as required by delta-3 G2. Never mix
  peers from different manifests or omit a peer ID.

## Evidence Path

- `artifacts/FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
