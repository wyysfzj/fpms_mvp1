# FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["lifecycle", "lineage", "ui", "api"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04.md
Chosen runbook: `P0-frontend-heavy-story`

## Fixed References

- Approved design: `docs/superpowers/specs/2026-08-26-fpms-demo-v6-ui-parity-design.md`,
  exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved implementation plan:
  `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-implementation.md`, exact commit
  `80bd46829eaf5f798dda9422550a583c7fa12fde`, Task 04 only.
- Active lean overlay:
  `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-lean-execution-overlay.md`.
- Accepted repaired Ordinal 03 HEAD: `3fc483d07d5992a91263b056e67355f7eae29e1b`.

## Exact Closure Slice

Close only the visible normal-UI inputs for V6 stages 03–05 by exposing existing lifecycle,
evidence, OA reply-link, and receipt-archive commands through same-case reviewed selectors. Remove raw
internal-ID entry from these paths. No backend lifecycle/service behavior changes.

## Exact Behavior

1. Filing preparation exposes `记录人工递交完成` with visible submission timestamp and note, calling
   the existing external-operation endpoint. The user never enters an attachment/document/internal
   ID and the existing non-demo flow remains intact.
2. Document detail renders one focused `DocumentLifecycleEvidenceActions` panel over existing
   acceptance, preliminary-start/pass, publication, and substantive-start lifecycle endpoints. Each
   action selects only current same-case `APPROVED` reviewed evidence by visible title/role/filename;
   source version/hash remain bound and are never inferred or typed by the user.
3. OA reply package links a reply document only through a visible selector of current same-case
   eligible reply documents, reusing `linkOaReplyDocument`. OA1 and OA2 can bind distinct visible
   documents; no raw document ID control remains.
4. Receipt archive replaces attachment-ID text entry with a visible filename/role selector limited
   to current same-case eligible reviewed attachments. OA1 and OA2 can archive distinct receipt
   attachments and retain both histories.
5. Missing, wrong-case, unreviewed, stale/hash-drifted, duplicate, or ineligible evidence fails
   closed in the affected action; the UI does not guess, silently substitute, or expose an unsafe
   command.
6. All new user-visible text is Simplified Chinese. Existing endpoint status, response, permission,
   idempotency, lifecycle, and evidence semantics remain unchanged.

## Explicit Non-Closure

- No backend/service/model/schema/migration/seed/source/state-machine/permission change; no direct
  HTTP/DB, mock, retry/reconcile redesign, generic evidence framework, page redesign, adjacent
  translation/cleanup, grant-fee stage 06, fee stages 07–11, release, or post-demo security task.
- Do not copy a second lifecycle panel for OA1/OA2. Do not add raw ID fallbacks, customer-decision
  controls, hidden demo command pages, `/demo/abc` behavior, or new normal-page mutations beyond the
  named existing endpoints.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04.md`
- `frontend/src/modules/cases/pages/FilingPreparation.vue`
- `frontend/src/modules/documents/pages/DocumentDetail.vue`
- `frontend/src/modules/documents/pages/OAReplyPackage.vue`
- `frontend/src/modules/documents/components/DocumentLifecycleEvidenceActions.vue`
- `frontend/src/modules/officialWorkflows/components/ReceiptArchivePanel.vue`
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/api/officialWorkflows.ts`
- `frontend/src/api/officialWorkflows.types.ts`
- `frontend/tests/demo-v6-lifecycle-ui-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04/**`

## Verification Commands

```bash
node frontend/tests/demo-v6-lifecycle-ui-contract.mjs
node frontend/tests/document-evidence-review-contract.mjs
node frontend/tests/oa-reply-checklist-actions.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/cases/pages/FilingPreparation.vue \
  src/modules/documents/pages/DocumentDetail.vue \
  src/modules/documents/pages/OAReplyPackage.vue \
  src/modules/documents/components/DocumentLifecycleEvidenceActions.vue \
  src/modules/officialWorkflows/components/ReceiptArchivePanel.vue \
  src/api/documents.ts src/api/documents.types.ts \
  src/api/officialWorkflows.ts src/api/officialWorkflows.types.ts)
git diff --check
```

GREEN must dynamically prove visible timestamp/note submission, same-case approved evidence
selection with version/hash binding, distinct OA1/OA2 reply/receipt selection, absence of raw ID
controls, unchanged request/error semantics, and wrong-case/unreviewed/stale fail-closed behavior.
Independent review binds the exact task range.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-LIFECYCLE-20260826-04/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-GRANT-20260826-05`, blocked until this task is accepted.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`, explicitly deferred until after the demo.

## Done Definition

Stages 03–05 can be performed through normal visible UI using current same-case reviewed evidence,
with no internal ID entry or backend change. Focused tests, typecheck, scoped ESLint, diff/scope,
independent zero-finding review, and atomic evidence gate pass.

## Rollback

Run `git revert --no-edit <accepted-task-range>`. Accepted session/observer behavior remains intact;
Ordinal 05 remains blocked.
