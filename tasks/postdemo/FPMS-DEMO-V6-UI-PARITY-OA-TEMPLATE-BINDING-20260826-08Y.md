# FPMS-DEMO-V6-UI-PARITY-OA-TEMPLATE-BINDING-20260826-08Y

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["demo", "ui", "lifecycle", "lineage", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OA-TEMPLATE-BINDING-20260826-08Y.md
Chosen runbook: `P0-frontend-heavy-story`

## Fixed References

- Approved design exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved implementation plan exact commit `80bd46829eaf5f798dda9422550a583c7fa12fde`.
- Accepted prerequisite HEAD `7c899e1a310cf1f520d4769d8a033dd31b216149`.
- User-approved prerequisite: bind the already-loaded authoritative document-template code into
  the existing lifecycle evidence actions before resuming Task 08.
- Active Task 08 is paused. Its disjoint uncommitted allowlist must remain byte-identical during
  Task 08Y.

## Root Cause and Hypothesis

The document mapping may omit `template_code` while `DocumentDetail` has already loaded the exact
template by `doc_template_id`. Passing that loaded template code into the existing lifecycle panel
lets its existing OA recognizer render the correct mode without changing mapping, API, or lifecycle
semantics.

## Exact Closure Slice

Pass the parent-loaded document-template code through one narrow prop and use it for the existing OA
mode recognition.

## Exact Behavior

1. `DocumentDetail` passes `docTemplate?.code` into `DocumentLifecycleEvidenceActions`, with only a
   safe existing document-code fallback where needed.
2. `DocumentLifecycleEvidenceActions` accepts one optional template-code prop and evaluates its
   existing `isOaNoticeTemplateCode` recognition against the parent value first, preserving the
   document fallback for its other existing caller.
3. A real focused browser test maps a document without `template_code`, loads template
   `OFFICIAL_NOTICE_003` in the parent, and proves the rendered child shows
   `已复核证据版本` plus `记录审查意见通知`.
4. The same real test proves an ordinary loaded template still shows `证据文件` and exactly the
   existing five ordinary lifecycle actions.

## Explicit Non-Closure

- No backend, API adapter/type, document mapping, store/state, helper/framework, lifecycle action,
  label, permission, schema, migration, seed, Stage 03 metadata, deadline preview, static AST test,
  or Task 08 behavior change.
- Do not re-review Stage 03 or deadline preview. Review cost is limited to the exact parent-child
  binding, its dynamic regression, and the two allowed product files.
- Do not modify or absorb the active Task 08 dirty baseline. Task 08 resumes only after Task 08Y
  independent acceptance.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OA-TEMPLATE-BINDING-20260826-08Y.md`
- `frontend/src/modules/documents/pages/DocumentDetail.vue`
- `frontend/src/modules/documents/components/DocumentLifecycleEvidenceActions.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-document-lifecycle-template-binding.spec.ts`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-OA-TEMPLATE-BINDING-20260826-08Y/**`

## Verification Commands

```bash
(cd FPMS_Automation_Skeleton_Pack/playwright_ts && \
  node ./node_modules/@playwright/test/cli.js test \
  src/tests/demo-v6-document-lifecycle-template-binding.spec.ts --workers=1)
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/documents/pages/DocumentDetail.vue \
  src/modules/documents/components/DocumentLifecycleEvidenceActions.vue --max-warnings 0)
git diff --check
```

RED is the real mounted document detail missing the OA label/action despite its loaded
`OFFICIAL_NOTICE_003` template. GREEN is that exact parent-child binding plus the unchanged ordinary
five-action regression. Do not run broad, strict, backend, static Stage 03, deadline-preview,
release, or repository-wide gates in Task 08Y.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-OA-TEMPLATE-BINDING-20260826-08Y/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`, resume after Task 08Y acceptance.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`, remains deferred until after the demo.

## Done Definition

The dynamic parent-child regression proves mapped OA and ordinary template behavior, focused gates
pass, active Task 08 bytes remain unchanged, and independent zero-finding review plus atomic
evidence accept only the exact Task 08Y range without re-reviewing adjacent Stage 03 or deadline
work.

## Rollback

Run `git revert --no-edit <accepted-08Y-range>`. Task 08 returns to its truthful mapped-OA control
absence RED.
