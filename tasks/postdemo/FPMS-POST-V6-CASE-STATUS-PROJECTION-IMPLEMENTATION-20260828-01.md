# FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["api", "legal", "lifecycle", "ui"]
Task-Path: tasks/postdemo/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01.md

## Approved Source Contract

- Commit: `814523a`
- Design: `docs/superpowers/specs/2026-08-28-case-list-lifecycle-projection-design.md`
- Plan: `docs/superpowers/plans/2026-08-28-case-list-lifecycle-projection.md`

## Exact Closure Slice

Project the existing case workflow status alias, authoritative lifecycle three-axis values,
and update timestamp through `GET /api/v1/cases`; preserve the legacy status contract; then
make the dashboard and two case-list tables describe workflow stage and workflow status
without changing the case-detail lifecycle display.

## Explicit Non-Closure

- No database schema or migration.
- No lifecycle transition, event, revision, or verification rule change.
- No removal or reinterpretation of `Case.status`.
- No application-date inference or historical backfill.
- No case-detail `CaseStepper` or three-track projection change.
- No new filter, report, store, request, state service, shared UI component, seed, runbook,
  fee-chain, deployment, or release work.

## Allowed Files

- `tasks/postdemo/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01.md`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_v3_workflow.py`
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/constants/workflow.ts`
- `frontend/src/constants/labels.zh.ts`
- `frontend/src/modules/cases/pages/CaseList.vue`
- `frontend/src/modules/dashboard/dashboard.api.ts`
- `frontend/src/modules/dashboard/components/WorkflowCaseTable.vue`
- `frontend/tests/case-list-lifecycle-projection-contract.mjs`
- `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01/**`

## Observable Acceptance

1. A list item returns `status`, equal `workflow_status`, the three lifecycle axes, and
   `updated_at` while preserving nullable `filing_date`.
2. Frontend maps an old-server response without `workflow_status` back to `status` and
   normalizes nullable `updated_at` to the existing empty-string public contract.
3. Dashboard groups by `workflow_status || status` and calls the fifth card “授权阶段”.
4. Both list tables show `GRANT_PENDING` as “第5阶段/5 · 授权登记” and label its badge
   “流程状态”.
5. Missing application date is shown as “待录入”.
6. `CaseStepper` and shared `getCaseWorkflow()` retain “授权 / 第5步/5”.

## Verification Commands

```bash
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 backend-test test -- -q tests/test_v3_workflow.py tests/test_pd_p1_case_official_fields_api.py
node frontend/tests/case-list-lifecycle-projection-contract.mjs
PATH="frontend/node_modules/.bin:$PATH" ./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 record frontend_typecheck -- vue-tsc --noEmit -p frontend/tsconfig.json
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 record lint -- ruff check backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_v3_workflow.py
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 record whitespace -- git diff --check
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 record scope -- python3 scripts/evidence_scope.py finalize FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01
```

## Remaining Follow-Up Task IDs

None — exact closure only.

## Evidence Path

- `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01/task.json`
- `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01/results.jsonl`
- `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01/summary.md`
- `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01/git/diff.patch`
- `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01/review/independent_review.md`

## Stop Conditions

Stop the affected lane if any value cannot be projected directly from existing `t_case`
columns, if implementation requires a lifecycle write or migration, or if preserving the
case-detail workflow contract requires redesign rather than the approved local list
projection.
