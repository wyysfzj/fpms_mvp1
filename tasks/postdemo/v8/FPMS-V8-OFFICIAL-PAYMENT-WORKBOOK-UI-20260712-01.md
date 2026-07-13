# FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `218`
Executor role: Frontend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `726`
- Expected manifest phase: `deferred`
- Customer gate requirement: `DG-PAYMENT-WORKBOOK[GLOBAL]`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: medium
- `chosen_runbook`: `P0-frontend-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-UI`

- RED expectation: Targeted Playwright fails on the named visible behavior.
- GREEN expectation: Targeted Playwright, exact-file ESLint and explicitly required `FE-TYPE` pass.

## Exact Closure Slice

One official-workbook generation/download capability; generated never implies official acceptance, payment or ticket verification.

## Explicit Non-Closure

No backend change, second page capability or frontend business-state calculation. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01`
- `FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01`
- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-FE-ADAPTER-20260712-01`

### External, gate and inherited prerequisites

- `gate` — `DG-PAYMENT-WORKBOOK:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.

- Approved source dependency cell (verbatim): FE adapter; serialized after Wave5 UI

### Shared ownership serialization

- `frontend/src/modules/annuity/pages/PayListDetail.vue` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01.md`
- `frontend/src/modules/annuity/pages/PayListDetail.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-official-payment-workbook-ui.spec.ts`
- `artifacts/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Require the exact persisted gate and lane activation; absent/revoked/future/scope-mismatched decisions are 409/no write.

## Verification Commands

- RED command: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-official-payment-workbook-ui.spec.ts --workers=1`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-official-payment-workbook-ui.spec.ts --workers=1`
- `cd frontend && npx eslint src/modules/annuity/pages/PayListDetail.vue --max-warnings 0`
- `git diff --check -- frontend/src/modules/annuity/pages/PayListDetail.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-official-payment-workbook-ui.spec.ts tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01` pass. Only then may this task be reported PASS.
