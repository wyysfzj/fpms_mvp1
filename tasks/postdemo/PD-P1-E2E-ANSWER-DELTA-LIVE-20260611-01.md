# PD-P1-E2E-ANSWER-DELTA-LIVE-20260611-01 — Live E2E answer delta coverage

## Exact Closure Slice

Update live-backend P1 Playwright coverage to verify 2026-06-11 answer deltas: total POA reuse/mapping visibility, OA PDF category “其他证明文件”, and fee reduction conversion display.

## Explicit Non-Closure

No backend product code. No frontend product code except test harness/fixtures if required. No contract-fixture fallback unless live backend is proven unstable and existing API evidence is cited.

## Remaining Follow-Up Task IDs

- `PD-P1-QA-FULLSCOPE-ANSWER-DELTA-20260611-01`

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/package.json`
- `tasks/postdemo/PD-P1-E2E-ANSWER-DELTA-LIVE-20260611-01.md`
- `artifacts/PD-P1-E2E-ANSWER-DELTA-LIVE-20260611-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run test:pd-p1`
- `./scripts/task_validate.sh PD-P1-E2E-ANSWER-DELTA-LIVE-20260611-01`

## Acceptance

- E2E sees “总委托书备案编号” for applicant/case filing readiness or mapping pending.
- E2E sees OA PDF category as “其他证明文件”.
- E2E sees fee conversion `0.85 -> 0.15` and does not expect “语义待确认”.
