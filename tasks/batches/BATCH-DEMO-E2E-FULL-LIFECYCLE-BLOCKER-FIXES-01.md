# BATCH-DEMO-E2E-FULL-LIFECYCLE-BLOCKER-FIXES-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Role

Lead / batch coordinator for true UI full-case-lifecycle blocker fixes.

## Source Of Truth

- Previous task: `tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-01.md`
- Previous evidence: `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01/**`
- Previous report: `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01/ui_full_lifecycle_e2e_report.md`
- Continue case for retry when feasible: `RUI202605100035`
- Skeleton mapping: `FPMS_Automation_Skeleton_Pack/data/testcases/by_wave/a.yaml`, `b.yaml`, `g0.yaml`, `d.yaml`, `f.yaml`

## Exact Closure Slice

Coordinate atomic blocker-fix tasks that unblock a true observable UI full-case-lifecycle retry for FPMS. This batch does not itself implement product changes; it defines task ownership, sequencing, and final QA retry scope.

## Explicit Non-Closure

- Do not implement a broad "fix all lifecycle" change in this batch file.
- Do not mutate business state through API during the final browser retry.
- Do not modify Skeleton Pack YAML/JSON/schema/source assets.
- Do not claim final full-lifecycle PASS until every atomic fix task has PASS evidence and the browser retry task passes.
- Do not run concurrent edits against shared files such as frontend API clients, backend billing service/API, document create flow, or grant-fee service.

## Batch Manifest

| Wave | Task file | Owner role | Closure slice | Shared ownership note |
| --- | --- | --- | --- | --- |
| 1 | `tasks/backend/business_logic/BL-E2E-DOC-TEMPLATE-DEADLINE-FALLBACK-01.md` | backend worker | UI-created OA_IN/OA_OUT documents use DocTemplate deadline/reply rules even when generic `doc_type` is present. | Serializes `backend/app/modules/tasks/task_generation_service.py`. |
| 1 | `tasks/frontend/DEMO-UI/FE-E2E-CASE-TASK-DONE-VISIBILITY-01.md` | frontend worker | Case detail task tab visibly shows generated and written-off tasks with Chinese status labels. | Runs after backend task generation contract is frozen. |
| 2 | `tasks/backend/business_logic/BL-E2E-GRANT-FEE-TASK-LIFECYCLE-01.md` | backend worker | GRANT_NOTICE creates/reuses a grant-fee task and grant-fee completion can drive final grant status when prerequisites exist. | Serializes document create side effects and grant-fee service. |
| 2 | `tasks/frontend/DEMO-UI/FE-E2E-GRANT-FEE-CASE-FILTER-01.md` | frontend worker | Grant-fee task list accepts visible case number filtering and displays case number. | Runs after backend grant-fee task query contract is available. |
| 3 | `tasks/frontend/DEMO-UI/FE-E2E-FEE-DRAFT-PAYLIST-SELECTION-01.md` | frontend worker | Locked fee draft official rows can be selected through visible UI and enable pay-list generation. | Frontend fees page only. |
| 4 | `tasks/backend/apis_ext/API-E2E-CASE-BILL-RECEIPT-SUMMARY-01.md` | backend worker | Case receipt summary returns bill rows even before a manual receipt exists. | Serializes billing API/schema tests before billing frontend mapping. |
| 4 | `tasks/frontend/DEMO-UI/FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01.md` | frontend worker | Case detail "账单与收款" tab maps and renders backend bill rows. | Depends on backend summary response. |
| 5 | `tasks/frontend/DEMO-UI/FE-E2E-CASE-RECEIPT-AMOUNT-INPUT-01.md` | frontend worker | Case receipt amount controls support observable keyboard/form input. | Frontend billing dialog only. |
| 6 | `tasks/backend/apis_ext/API-E2E-PAYMENT-OFFSET-LINKAGE-01.md` | backend worker | Payment created from a bill is linkable to bill/case for visible payment and offset flow. | Serializes billing service/API/schema changes. |
| 6 | `tasks/frontend/DEMO-UI/FE-E2E-PAYMENT-OFFSET-VISIBILITY-01.md` | frontend worker | Payment/offset UI can filter or prefill target bill/case and create visible offset. | Depends on backend payment linkage. |
| 7 | `tasks/backend/business_logic/BL-E2E-ANNUITY-TARGETED-GENERATION-01.md` | backend worker | Granted case supports targeted annuity generation and case-number query. | Depends on final grant status contract. |
| 7 | `tasks/frontend/DEMO-UI/FE-E2E-ANNUITY-TARGETED-GENERATION-01.md` | frontend worker | Annuity task page/dialog visibly binds current case filter before generation. | Depends on backend annuity query/generation contract. |
| 8 | `tasks/backend/apis_ext/API-E2E-COMMISSION-SETTLEMENT-CASE-FILTER-01.md` | backend worker | Commission settlement report/generation path can resolve target case number. | Runs after payment/settleable recompute. |
| 8 | `tasks/frontend/DEMO-UI/FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01.md` | frontend worker | Commission settlement page exposes visible target-case query/generation path. | Depends on backend settlement case filter. |
| 9 | `tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01.md` | QA monitor/main | Rerun true observable browser-use full lifecycle validation. | Runs only after fix tasks are PASS. |

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-FULL-LIFECYCLE-BLOCKER-FIXES-01 lint /bin/zsh -lc 'test -f tasks/batches/BATCH-DEMO-E2E-FULL-LIFECYCLE-BLOCKER-FIXES-01.md'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-FULL-LIFECYCLE-BLOCKER-FIXES-01 test /bin/zsh -lc 'for f in tasks/backend/business_logic/BL-E2E-DOC-TEMPLATE-DEADLINE-FALLBACK-01.md tasks/frontend/DEMO-UI/FE-E2E-CASE-TASK-DONE-VISIBILITY-01.md tasks/backend/business_logic/BL-E2E-GRANT-FEE-TASK-LIFECYCLE-01.md tasks/frontend/DEMO-UI/FE-E2E-GRANT-FEE-CASE-FILTER-01.md tasks/frontend/DEMO-UI/FE-E2E-FEE-DRAFT-PAYLIST-SELECTION-01.md tasks/backend/apis_ext/API-E2E-CASE-BILL-RECEIPT-SUMMARY-01.md tasks/frontend/DEMO-UI/FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01.md tasks/frontend/DEMO-UI/FE-E2E-CASE-RECEIPT-AMOUNT-INPUT-01.md tasks/backend/apis_ext/API-E2E-PAYMENT-OFFSET-LINKAGE-01.md tasks/frontend/DEMO-UI/FE-E2E-PAYMENT-OFFSET-VISIBILITY-01.md tasks/backend/business_logic/BL-E2E-ANNUITY-TARGETED-GENERATION-01.md tasks/frontend/DEMO-UI/FE-E2E-ANNUITY-TARGETED-GENERATION-01.md tasks/backend/apis_ext/API-E2E-COMMISSION-SETTLEMENT-CASE-FILTER-01.md tasks/frontend/DEMO-UI/FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01.md tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-01.md; do test -f "$f" || exit 1; done'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-FULL-LIFECYCLE-BLOCKER-FIXES-01 task_gate ./scripts/task_validate.sh BATCH-DEMO-E2E-FULL-LIFECYCLE-BLOCKER-FIXES-01
```

## Evidence Path

- `artifacts/BATCH-DEMO-E2E-FULL-LIFECYCLE-BLOCKER-FIXES-01/results.jsonl`
- `artifacts/BATCH-DEMO-E2E-FULL-LIFECYCLE-BLOCKER-FIXES-01/summary.md`
- `artifacts/BATCH-DEMO-E2E-FULL-LIFECYCLE-BLOCKER-FIXES-01/git/diff.patch`
- `artifacts/BATCH-DEMO-E2E-FULL-LIFECYCLE-BLOCKER-FIXES-01/root_cause.md`

## Remaining Follow-Up Task IDs

- `BATCH-DEMO-E2E-FULL-LIFECYCLE-BLOCKER-FIXES-01-FOLLOW-UP-UNSUPPORTED-UI` if final retry still finds unsupported UI lifecycle steps.

## Done Definition

This batch is PASS only when every listed atomic task has independent PASS evidence and the final retry task reaches PASS through visible UI-only business mutations. Otherwise the batch remains BLOCKED or FAIL according to the first unresolved task.

