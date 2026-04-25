# BATCH-FE-COMPLETENESS-REMEDIATION-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Coordinate FE completeness remediation from audit to readiness, blocker drain,
frontend capability landing, and close audit.

This batch closes only the remediation items explicitly listed in the readiness
and blocker drain manifest. Each implementation item must still be executed as
one atomic task file with independent evidence.

## Explicit Non-Closure

Do not implement unrelated frontend refactors. Do not change backend behavior
inside frontend tasks. Do not fake frontend completion for unavailable backend
capabilities. Do not run concurrent edits against shared route/menu/API files.

## Wave Order

1. Readiness Gate
2. Blocker Drain
3. FE Capability Landing
4. Close Audit

## Task File Paths

- tasks/frontend/audit/FE-COMPLETENESS-AUDIT-DOC-01.md
- tasks/frontend/FE-FEE-APPLY-FEE-GENERATE-01.md
- tasks/frontend/FE-PAYLIST-FROM-FEE-ITEMS-01.md
- tasks/frontend/FE-PAYLIST-DETAIL-ENTRY-01.md
- tasks/frontend/FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01.md
- tasks/frontend/FE-BILL-DIRECTION-VISIBILITY-01.md
- tasks/frontend/FE-PAYMENT-CREATE-ENTRY-01.md
- tasks/frontend/FE-COMMISSION-SETTLEABILITY-VISIBILITY-01.md
- tasks/frontend/FE-MENU-PERMISSION-ALIGNMENT-01.md
- tasks/batches/BATCH-FE-COMPLETENESS-REMEDIATION-01-CLOSE-AUDIT.md

## Shared File Serialization Decisions

- `frontend/src/api/fees.ts` and `frontend/src/api/fees.types.ts`: serialized under FE-FEE-APPLY-FEE-GENERATE-01.
- `frontend/src/api/govPayments.ts` and `frontend/src/api/govPayments.types.ts`: serialized under pay-list/gov-payment tasks.
- `frontend/src/api/commission.ts` and `frontend/src/api/commission.types.ts`: serialized under commission visibility task.
- `frontend/src/constants/menu.ts`: serialized under menu permission alignment task.
- Route changes are avoided unless readiness proves they are necessary.

## Verification Commands

```bash
cd frontend && npm run typecheck
cd frontend && npm run build
./scripts/task_validate.sh <TASK-ID>
```

## Evidence Path

- artifacts/BATCH-FE-COMPLETENESS-REMEDIATION-01/results.jsonl
- artifacts/BATCH-FE-COMPLETENESS-REMEDIATION-01/summary.md
- artifacts/BATCH-FE-COMPLETENESS-REMEDIATION-01/git/diff.patch

## Remaining Follow-Up Task IDs

None for the readiness slice. Implementation follow-ups are listed in
`tasks/batches/BATCH-FE-COMPLETENESS-BLOCKER-DRAIN-01.md`.
