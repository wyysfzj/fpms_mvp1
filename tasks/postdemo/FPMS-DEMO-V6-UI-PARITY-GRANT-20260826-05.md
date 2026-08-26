# FPMS-DEMO-V6-UI-PARITY-GRANT-20260826-05

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["lifecycle", "lineage", "fee", "ui", "api"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-GRANT-20260826-05.md
Chosen runbook: `P0-frontend-heavy-story`

## Fixed References

- Approved design exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved implementation plan exact commit `80bd46829eaf5f798dda9422550a583c7fa12fde`,
  Task 05 only, under the active lean overlay.
- Accepted Ordinal 04 HEAD: `ef71b46850754a3f6fe8abb7f2a97ff286923e11`.
- The Task 04 shared `DocumentLifecycleEvidenceActions` component is now owned by this serialized task.

## Exact Closure Slice

Close only the visible normal-UI Stage 06 inputs for original/replacement grant-notice evidence and
the existing current-task `标记等待客户` command. Reuse existing endpoints, lifecycle state, evidence
lineage, correction, preview, and PAY behavior.

## Exact Behavior

1. From the current grant-fee task row, the user can select an original or replacement grant notice
   only by visible title/role/filename from current same-case `APPROVED` reviewed evidence. The action
   binds the exact source version/hash and calls the existing grant-notice lifecycle endpoint.
2. Original and replacement notices remain distinct visible evidence. After correction, the old task
   is read-only and cannot confirm, wait, preview, or PAY; the current confirmed task alone exposes
   `标记等待客户` when `allowed_actions` permits it.
3. `标记等待客户` reuses the existing `mark_waiting_client` action. Unconfirmed, superseded, wrong-case,
   unreviewed, stale/hash-drifted, duplicate, or ambiguous evidence/tasks fail closed without HTTP.
4. PAY remains exactly once and existing correction/preview controls and responses remain unchanged.
   The UI does not infer document role, request internal IDs, or add a customer-decision panel.
5. Existing endpoint status, response, permission, idempotency, lifecycle, evidence, and official-fee
   semantics are unchanged. New visible text is Simplified Chinese.

## Explicit Non-Closure

- No backend/service/model/schema/migration/seed/source/fee-rate/preview/state-machine/permission
  change; no new endpoint, raw ID input, generic evidence component, duplicate grant workflow,
  customer-decision UI, Stage 07 confirmation, Stage 08–11 work, broad test, release, or post-demo
  security task.
- Do not absorb adjacent task-list refactoring, status translation, styling, or unrelated cleanup.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-GRANT-20260826-05.md`
- `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `frontend/src/modules/documents/components/DocumentLifecycleEvidenceActions.vue`
- `frontend/src/api/grantFees.ts`
- `frontend/src/api/grantFees.types.ts`
- `frontend/tests/demo-v6-grant-ui-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-GRANT-20260826-05/**`

## Verification Commands

```bash
node frontend/tests/demo-v6-grant-ui-contract.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/grantFees/pages/GrantFeeTaskList.vue \
  src/modules/documents/components/DocumentLifecycleEvidenceActions.vue \
  src/api/grantFees.ts src/api/grantFees.types.ts)
(cd backend && PYTHONPATH=. \
  /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python -m pytest -q \
  tests/test_demo_integrated_grant.py tests/test_demo_v6_grant_official_fee.py \
  tests/test_v8_grant_notice_lifecycle_api.py \
  tests/test_v8_grant_evidence_accepted_dispatch.py \
  -k 'not test_ia10_to_ia12_are_real_and_next_red_is_ia13')
git diff --check
```

Baseline variance: `test_ia10_to_ia12_are_real_and_next_red_is_ia13` is a pre-existing stale source
assertion that still requires `return this.red('IA-13')`, while the accepted baseline already
implements IA-13 and IA-14. Its failure must be recorded separately and is not absorbed into this
frontend-only Stage 06 task; every other test in the four frozen files remains required.

GREEN must dynamically prove distinct source-bound original/replacement notice selection, exact
same-case approved/current/final/hash eligibility, old-task read-only behavior, current confirmed
`mark_waiting_client`, unchanged PAY/correction/preview behavior, duplicate/ambiguous no-call, and
original error identity. Independent review binds the exact task range.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-GRANT-20260826-05/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-FEE-20260826-06`, blocked until this task is accepted.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`, deferred until after the demo.

## Done Definition

Stage 06 runs through visible normal UI with exact reviewed grant-notice lineage and correct current
task actions, without raw IDs or backend change. Focused frontend/backend tests, typecheck, scoped
ESLint, diff/scope, independent zero-finding review, and atomic evidence pass.

## Rollback

Run `git revert --no-edit <accepted-task-range>`. Ordinal 04 remains accepted; Ordinal 06 stays
blocked.
