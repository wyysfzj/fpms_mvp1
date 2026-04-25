# BATCH-B-BLOCKER-DRAIN-03

Batch ID: `BATCH-B-BLOCKER-DRAIN-03`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

chosen_runbook: `P0-prereq-heavy-story`

## Goal

Drain the remaining B-wave backend blockers before resuming automation landing:

- `TC-B-009`: `BE-B-OA-FEE-ITEM-LIST-SCHEMA-01`
- `TC-B-010/011`: `BE-B-OA-BILL-PAYMENT-READINESS-01`
- `TC-B-012`: `BE-B-OA-COMMISSION-READINESS-01`
- `TC-B-013`: `BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01`

## Execution Order

1. `BE-B-OA-FEE-ITEM-LIST-SCHEMA-01`
2. `BE-B-OA-BILL-PAYMENT-READINESS-01`
3. `BE-B-OA-COMMISSION-READINESS-01`
4. `BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01`

`BE-B-OA-BILL-PAYMENT-READINESS-01` and `BE-B-OA-COMMISSION-READINESS-01` depend on stable OA fee item list exposure from `BE-B-OA-FEE-ITEM-LIST-SCHEMA-01`.

## Shared File Decisions

- `backend/app/modules/fees/schemas.py` is owned only by `BE-B-OA-FEE-ITEM-LIST-SCHEMA-01`.
- `backend/app/modules/billing/*` is owned only by `BE-B-OA-BILL-PAYMENT-READINESS-01`.
- `backend/app/modules/commission/*` is owned only by `BE-B-OA-COMMISSION-READINESS-01`.
- `backend/app/modules/documents/service.py` and `backend/app/modules/documents/schemas.py` are owned only by `BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01`.
- SQLite write tests run serially.

## Explicit Non-Closure

Do not implement B-wave pytest automation handlers in this batch.
Do not modify `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py`.
Do not modify frontend or skeleton data.
Do not combine OA fee list, bill/payment, commission, and NeedReply/deadline edits into one atomic closure.

## Evidence

- `artifacts/BATCH-B-BLOCKER-DRAIN-03/results.jsonl`
- `artifacts/BATCH-B-BLOCKER-DRAIN-03/summary.md`
- `artifacts/BATCH-B-BLOCKER-DRAIN-03/git/diff.patch`
