# PD-P1-FE-FEE-REDUCTION-CONVERSION-20260611-01 — Fee reduction conversion UI

## Exact Closure Slice

Update P1 fee linkage UI and frontend API types to show customer “减免比例” and computed “应缴比例” distinctly, using the backend conversion contract.

## Explicit Non-Closure

No backend code. No payment execution. No official Excel export implementation. No fee-rate seed data.

## Remaining Follow-Up Task IDs

- `PD-P1-E2E-ANSWER-DELTA-LIVE-20260611-01`

## Allowed Files

- `frontend/src/api/officialWorkflows.types.ts`
- `frontend/src/modules/officialWorkflows/components/FeeLinkagePanel.vue`
- `tasks/postdemo/PD-P1-FE-FEE-REDUCTION-CONVERSION-20260611-01.md`
- `artifacts/PD-P1-FE-FEE-REDUCTION-CONVERSION-20260611-01/**`

## Verification Commands

- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Browser smoke or Playwright targeted check for `0.85 减免 -> 0.15 应缴`.
- `./scripts/task_validate.sh PD-P1-FE-FEE-REDUCTION-CONVERSION-20260611-01`

## Acceptance

- UI no longer says `0 / 0.7 / 0.85` semantics are待确认.
- UI displays distinct labels for customer reduction ratio and payable ratio.
- Official template/source blockers remain visible as pending where appropriate.
