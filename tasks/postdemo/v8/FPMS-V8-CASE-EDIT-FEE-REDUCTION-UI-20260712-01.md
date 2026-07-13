# FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `101`
Executor role: Frontend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `524`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: high
- `evidence_cost`: medium
- `chosen_runbook`: `P0-frontend-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-UI`

- RED expectation: Targeted Playwright fails on the named visible behavior.
- GREEN expectation: Targeted Playwright, exact-file ESLint and explicitly required `FE-TYPE` pass.

## Exact Closure Slice

Edit page preserves unknown/unset legacy input as a blocking warning, displays/sends only an explicit canonical selection, and never coerces missing data to `0`.

## Explicit Non-Closure

No backend change, second page capability or frontend business-state calculation. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01`
- `FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): update API; serialized after create UI

### Shared ownership serialization

- `frontend/src/api/cases.ts` order key `4`; project this order only across owners present in the active manifest.
- `frontend/src/api/cases.types.ts` order key `4`; project this order only across owners present in the active manifest.
- `frontend/src/modules/cases/pages/CaseEdit.vue` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01.md`
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/modules/cases/pages/CaseEdit.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-edit-fee-reduction.spec.ts`
- `artifacts/FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-edit-fee-reduction.spec.ts --workers=1`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-edit-fee-reduction.spec.ts --workers=1`
- `cd frontend && npx eslint src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseEdit.vue --max-warnings 0`
- `git diff --check -- frontend/src/api/cases.ts frontend/src/api/cases.types.ts frontend/src/modules/cases/pages/CaseEdit.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-edit-fee-reduction.spec.ts tasks/postdemo/v8/FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01` pass. Only then may this task be reported PASS.
