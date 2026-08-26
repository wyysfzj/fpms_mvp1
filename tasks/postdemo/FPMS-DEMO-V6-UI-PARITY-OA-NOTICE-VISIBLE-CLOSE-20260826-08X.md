# FPMS-DEMO-V6-UI-PARITY-OA-NOTICE-VISIBLE-CLOSE-20260826-08X

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["ui", "lifecycle", "lineage", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OA-NOTICE-VISIBLE-CLOSE-20260826-08X.md
Chosen runbook: `P0-single-lane-story`

## Fixed References

- Accepted pre-task HEAD `482d4f8a29f6ed11fc2e091b6aca05971edc4954`.
- Existing backend OA-notice endpoint and accepted OA template semantics are read-only authority.
- Active Task 08 has nine disjoint dirty files that must remain byte-identical.

## Exact Closure Slice

Close only the visible OA-notice lifecycle action and the OA official-deadline impact-preview request
boundary in the existing document UI.

## Exact Behavior

1. A recognized OA-notice template document exposes selector label `已复核证据版本` and visible
   action `记录审查意见通知`. The action uses the existing lifecycle evidence seam and calls
   `/documents/{id}/lifecycle/oa-notice` with current, same-case, approved final evidence plus the
   existing timing payload.
2. The authoritative accepted OA template code set is mirrored minimally from backend semantics.
   Non-OA documents retain the existing five lifecycle actions and labels unchanged. Stage 05
   continues to reuse this single component and API seam; no duplicate action is added.
3. On `DocumentCreate`, a recognized OA official notice sends zero impact-preview requests while
   any member of `official_due_date`, `official_due_date_source`, and
   `official_due_date_status` is incomplete. Once the triplet is complete, it sends one current
   preview request. Stale in-flight preview responses cannot replace the current state.
4. Ordinary document preview behavior remains unchanged, and incomplete OA deadline input causes
   no transient 409/400 UI or network response.

## Explicit Non-Closure

- No backend, endpoint, API permission, state, schema, migration, database, generic framework,
  debounce, duplicate Stage 05 flow, Task 08 change, or adjacent cleanup.
- Do not run broad or strict test suites.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OA-NOTICE-VISIBLE-CLOSE-20260826-08X.md`
- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `frontend/src/modules/documents/components/DocumentLifecycleEvidenceActions.vue`
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/tests/demo-v6-lifecycle-ui-contract.mjs`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-create-ui.spec.ts`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-OA-NOTICE-VISIBLE-CLOSE-20260826-08X/**`

## Verification Commands

```bash
node frontend/tests/demo-v6-lifecycle-ui-contract.mjs
(cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-document-deadline-create-ui.spec.ts --workers=1)
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/documents/pages/DocumentCreate.vue src/modules/documents/components/DocumentLifecycleEvidenceActions.vue src/api/documents.ts src/api/documents.types.ts tests/demo-v6-lifecycle-ui-contract.mjs)
git diff --check
```

RED comprises the focused OA lifecycle endpoint/action contract and the executable deadline UI
contract proving an incomplete triplet currently reaches preview. GREEN closes only these two
boundaries and preserves the existing five actions and ordinary-document behavior.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-OA-NOTICE-VISIBLE-CLOSE-20260826-08X/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08` resumes only after 08X acceptance.

## Done Definition

The OA reviewed-evidence action is visible and reaches the existing endpoint, incomplete OA deadline
input causes no preview request, the focused checks pass, all nine Task 08 dirty files remain
byte-identical, and independent review plus atomic evidence accept the exact 08X range.

## Rollback

Run `git revert --no-edit <accepted-08X-range>`. The visible OA close returns to its prior gap.
