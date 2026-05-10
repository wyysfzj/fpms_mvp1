# BATCH-DEMO-E2E-NEWCASE-BLOCKER-FIXES-02

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: high
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Role

Lead / batch coordinator for blockers found by `BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01`.

## Source Of Truth

- Previous task: `tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01.md`
- Previous evidence: `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/**`
- Previous report: `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/ui_full_lifecycle_e2e_report.md`
- New case: `RUI20260510033534`

## Exact Closure Slice

Coordinate atomic fixes for the blockers and directly related diagnostics from the latest true observable full-case-lifecycle UI E2E new-case run, then run one visible UI retry slice that proves the blocked checkpoints are no longer blocked.

## Explicit Non-Closure

- Do not implement a broad "fix full lifecycle" task in this batch file.
- Do not mutate business state through API during browser validation.
- Do not modify Skeleton Pack YAML/JSON/schema/source assets.
- Do not claim final PASS until every implementation task has independent evidence and the browser retry visibly completes the formerly blocked checkpoints.
- Do not run concurrent edits against shared frontend API clients or backend commission service/API files.

## Batch Manifest

| Wave | Task file | Owner role | Closure slice | Shared ownership note |
| --- | --- | --- | --- | --- |
| 0 | `tasks/frontend/DEMO-UI/FE-FEE-DRAFT-CURRENCY-STYLE-01.md` | frontend worker | Fee draft detail/list money rendering tolerates blank or invalid currency values without throwing `Currency code is required with currency style`. | Runs first because it may share a money-format helper with bill detail. |
| 1 | `tasks/frontend/DEMO-UI/FE-BILL-DETAIL-NETWORK-ERROR-NEW-BILL-01.md` | frontend worker | New bill detail renders the bill instead of showing `Network Error` when currency data is blank/invalid or supplementary offsets fail. | Serializes billing detail page changes after currency helper is available. |
| 2 | `tasks/frontend/DEMO-UI/FE-FEE-DRAFT-CASE-NO-FILTER-01.md` | frontend worker | Fee draft list "案件编号" filter can locate drafts by visible case number. | Serializes `frontend/src/api/fees.ts` changes. |
| 3 | `tasks/backend/apis_ext/API-E2E-COMMISSION-SETTLEMENT-UNASSIGNED-CASE-01.md` | backend worker | Commission settlement generation supports the E2E target case when the commission record has no agent assigned. | Serializes backend commission service/API/tests. |
| 4 | `tasks/frontend/DEMO-UI/FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01.md` | frontend worker | Commission settlement page gives a visible target-case path to create/select a batch and generate settlement lines for the target case. | Depends on backend unassigned-case generation behavior. |
| 5 | `tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01.md` | QA monitor/main | Browser-use retry validates the formerly blocked bill detail and commission settlement checkpoints through visible UI only. | Runs only after fix tasks have PASS evidence. |

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-NEWCASE-BLOCKER-FIXES-02 lint /bin/zsh -lc 'test -f tasks/batches/BATCH-DEMO-E2E-NEWCASE-BLOCKER-FIXES-02.md'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-NEWCASE-BLOCKER-FIXES-02 test /bin/zsh -lc 'for f in tasks/frontend/DEMO-UI/FE-FEE-DRAFT-CURRENCY-STYLE-01.md tasks/frontend/DEMO-UI/FE-BILL-DETAIL-NETWORK-ERROR-NEW-BILL-01.md tasks/frontend/DEMO-UI/FE-FEE-DRAFT-CASE-NO-FILTER-01.md tasks/backend/apis_ext/API-E2E-COMMISSION-SETTLEMENT-UNASSIGNED-CASE-01.md tasks/frontend/DEMO-UI/FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01.md tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-FIX-RETRY-01.md; do test -f "$f" || exit 1; done'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-NEWCASE-BLOCKER-FIXES-02 task_gate ./scripts/task_validate.sh BATCH-DEMO-E2E-NEWCASE-BLOCKER-FIXES-02
```

## Evidence Path

- `artifacts/BATCH-DEMO-E2E-NEWCASE-BLOCKER-FIXES-02/results.jsonl`
- `artifacts/BATCH-DEMO-E2E-NEWCASE-BLOCKER-FIXES-02/summary.md`
- `artifacts/BATCH-DEMO-E2E-NEWCASE-BLOCKER-FIXES-02/git/diff.patch`
- `artifacts/BATCH-DEMO-E2E-NEWCASE-BLOCKER-FIXES-02/root_cause.md`

## Remaining Follow-Up Task IDs

- `BATCH-DEMO-E2E-NEWCASE-BLOCKER-FIXES-02-FOLLOW-UP-UNSUPPORTED-UI` if final browser retry finds a new unsupported lifecycle UI step.

## Done Definition

This batch is PASS only when every listed atomic task has independent PASS evidence and the final browser retry reaches PASS for the formerly blocked checkpoints using visible UI-only business mutations. Otherwise the batch remains BLOCKED or FAIL according to the first unresolved task.
