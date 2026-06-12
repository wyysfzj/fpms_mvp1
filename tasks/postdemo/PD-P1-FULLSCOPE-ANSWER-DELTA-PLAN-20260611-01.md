# PD-P1-FULLSCOPE-ANSWER-DELTA-PLAN-20260611-01 — P1 answer-delta full-scope plan

## Exact Closure Slice

Review the current P1 implementation evidence against the 2026-06-11 customer answers, then produce a full-scope delta ledger and atomic implementation manifest for the remaining application enhancement work.

## Explicit Non-Closure

No backend product code changes. No frontend product code changes. No database migration changes. No CPC/OA direct submit, RPA, auto-signature, auto-payment, automatic email sending, or execution of the implementation tasks listed by this planning task.

## Story Shape Classification

| Field | Value |
| --- | --- |
| shared_file_density | High. Remaining deltas touch Alembic revisions, applicant masterdata, cases/official workflow APIs, fee linkage contracts, frontend API types, Vue pages, and Playwright fixtures. |
| prereq_dependency_density | High. Total POA and fee conversion carriers must precede API/service/UI/E2E verification. |
| be_fe_coupling | High. AC-17/AC-18 require backend contract and frontend display consistency. |
| evidence_cost | High. Completion requires per-task gates plus final AC-01..AC-18 close audit. |

chosen_runbook: `P0-prereq-heavy-story`

## Assumptions

- The active `/goal` is treated as approval to proceed through planning and then atomic implementation unless a blocker or scope conflict appears.
- Existing 2026-06-01 P1 task evidence remains valid for the original P1 scope, but it does not prove the 2026-06-11 answer deltas.
- Total POA source of truth should start on official applicant masterdata because cases already link `T_CaseApplicant.applicant_id` to `t_applicant`.
- Existing `Case.fee_reduction` remains the apply-fee payable-ratio field for older contracts; P1 answer delta adds an explicit conversion/readiness layer rather than silently reinterpreting all legacy values.

## Allowed Files

- `tasks/postdemo/PD-P1-FULLSCOPE-ANSWER-DELTA-PLAN-20260611-01.md`
- `tasks/postdemo/PD-P1-DB-APPLICANT-TOTAL-POA-20260611-01.md`
- `tasks/postdemo/PD-P1-BE-APPLICANT-TOTAL-POA-API-20260611-01.md`
- `tasks/postdemo/PD-P1-FE-APPLICANT-TOTAL-POA-UI-20260611-01.md`
- `tasks/postdemo/PD-P1-BE-FILING-TOTAL-POA-READINESS-20260611-01.md`
- `tasks/postdemo/PD-P1-BE-FEE-REDUCTION-CONVERSION-20260611-01.md`
- `tasks/postdemo/PD-P1-FE-FEE-REDUCTION-CONVERSION-20260611-01.md`
- `tasks/postdemo/PD-P1-E2E-ANSWER-DELTA-LIVE-20260611-01.md`
- `tasks/postdemo/PD-P1-QA-FULLSCOPE-ANSWER-DELTA-20260611-01.md`
- `docs/superpowers/plans/2026-06-11-postdemo-p1-answer-delta-full-scope.md`
- `artifacts/PD-P1-FULLSCOPE-ANSWER-DELTA-PLAN-20260611-01/**`

## Verification Commands

- `./scripts/evidence_run.sh PD-P1-FULLSCOPE-ANSWER-DELTA-PLAN-20260611-01 lint /bin/zsh -lc 'test -s docs/superpowers/plans/2026-06-11-postdemo-p1-answer-delta-full-scope.md && test -s artifacts/PD-P1-FULLSCOPE-ANSWER-DELTA-PLAN-20260611-01/analysis/full_scope_delta_ledger.md && test -s artifacts/PD-P1-FULLSCOPE-ANSWER-DELTA-PLAN-20260611-01/analysis/execution_manifest.md'`
- `./scripts/evidence_run.sh PD-P1-FULLSCOPE-ANSWER-DELTA-PLAN-20260611-01 test /bin/zsh -lc 'rg -n "AC-17|AC-18|总委托书备案编号|其他证明文件|0\\.85.*0\\.15|P0-prereq-heavy-story" docs/superpowers/plans/2026-06-11-postdemo-p1-answer-delta-full-scope.md artifacts/PD-P1-FULLSCOPE-ANSWER-DELTA-PLAN-20260611-01/analysis/*.md tasks/postdemo/PD-P1-*-20260611-01.md'`
- `./scripts/task_validate.sh PD-P1-FULLSCOPE-ANSWER-DELTA-PLAN-20260611-01`

## Evidence Path

- `artifacts/PD-P1-FULLSCOPE-ANSWER-DELTA-PLAN-20260611-01/**`

## Acceptance

- Full-scope delta ledger maps AC-01 through AC-18 to prior evidence, answer-delta impact, residual gaps, and planned task IDs.
- Atomic implementation manifest lists one closure slice per task, wave order, allowlists, verification, and non-scope.
- The plan explicitly preserves P1 non-scope: no direct submit, RPA, auto-signature, auto-payment, or Longxia replacement.
