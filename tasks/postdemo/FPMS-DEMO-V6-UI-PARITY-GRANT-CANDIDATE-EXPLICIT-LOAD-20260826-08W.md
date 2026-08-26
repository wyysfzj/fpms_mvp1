# FPMS-DEMO-V6-UI-PARITY-GRANT-CANDIDATE-EXPLICIT-LOAD-20260826-08W

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["demo", "ui", "lineage", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-GRANT-CANDIDATE-EXPLICIT-LOAD-20260826-08W.md
Chosen runbook: `P0-frontend-heavy-story`

## Fixed References

- Approved design exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved implementation plan exact commit `80bd46829eaf5f798dda9422550a583c7fa12fde`.
- Accepted prerequisite Task 08V HEAD `30b3478b7a6eedb0a3a3631a511c1ae1994f04b7`.
- User-approved prerequisite: make the optional grant-evidence candidate query explicitly
  user-triggered before resuming Task 08.
- Active Task 08 is paused. Its disjoint uncommitted allowlist must remain byte-identical during
  Task 08W.

## Root Cause and Hypothesis

The grant evidence review panel currently issues its optional candidate GET during ordinary
document-detail mount. Deferring that existing query until a visible user action prevents an
optional source/configuration failure from creating an initial error banner or false empty-state
claim while preserving every existing server and review semantic once candidates are requested.

## Exact Closure Slice

Make the existing `GrantEvidenceReviewPanel` candidate list load explicit and user-triggered.

## Exact Behavior

1. Ordinary document detail mount issues no grant-evidence candidate GET, shows no candidate API
   error banner, and does not claim `暂无授权证据候选` before any load attempt.
2. Before the first load, the panel shows the Simplified Chinese button
   `加载授权证据候选`. Clicking it invokes exactly one existing
   `listGrantEvidenceCandidates(documentId)` request.
3. After the first load attempt, the button uses the existing `刷新候选` semantics. Successful
   load, empty result, 200/409/permission/source-gate errors, review actions, and the existing
   post-review refresh remain unchanged.
4. Focused Playwright proves no candidate GET before the explicit click, truthful unloaded state,
   exactly one candidate GET after the click, and the complete existing second-person review path.

## Explicit Non-Closure

- No `DocumentDetail`, backend, endpoint, API adapter/type, permission, source gate, status/envelope,
  evidence review, routing, schema, migration, seed, business semantic, generic lazy-loading
  framework, broad UI cleanup, or Task 08 behavior change.
- Do not modify or absorb the active Task 08 dirty baseline. Task 08 resumes only after Task 08W
  independent acceptance.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-GRANT-CANDIDATE-EXPLICIT-LOAD-20260826-08W.md`
- `frontend/src/modules/documents/components/GrantEvidenceReviewPanel.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-grant-evidence-review-ui.spec.ts`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-GRANT-CANDIDATE-EXPLICIT-LOAD-20260826-08W/**`

## Verification Commands

```bash
(cd FPMS_Automation_Skeleton_Pack/playwright_ts && \
  node ./node_modules/@playwright/test/cli.js test \
  src/tests/v8-grant-evidence-review-ui.spec.ts --workers=1)
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/documents/components/GrantEvidenceReviewPanel.vue \
  --max-warnings 0)
git diff --check
```

RED is the focused browser test observing an initial candidate GET or the missing explicit-load
button. GREEN is the explicit load, one GET, and unchanged full review path. Do not run broad,
strict, backend, release, or repository-wide gates in Task 08W.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-GRANT-CANDIDATE-EXPLICIT-LOAD-20260826-08W/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`, resume after Task 08W acceptance.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`, remains deferred until after the demo.

## Done Definition

Ordinary document mount is truthful and performs no optional candidate query, one explicit user
click loads the existing candidates, the focused review journey and scoped checks pass, active Task
08 bytes remain unchanged, and independent zero-finding review plus atomic evidence accept the
exact Task 08W range.

## Rollback

Run `git revert --no-edit <accepted-08W-range>`. Task 08 returns to its truthful optional-source
initial-load RED.
