# FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `118`
Executor role: Frontend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `555`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: high
- `evidence_cost`: medium
- `chosen_runbook`: `P0-frontend-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-UI`

- RED expectation: Targeted Playwright fails on the named visible behavior.
- GREEN expectation: Targeted Playwright, exact-file ESLint and explicitly required `FE-TYPE` pass.

## Exact Closure Slice

FeeDraft create page reads explicit `obligation_id` from `/fees/drafts/new?obligation_id=...`, fetches source/instruction detail, and blocks manual draft unless status is PAY; it never guesses an obligation.

## Explicit Non-Closure

No backend change, second page capability or frontend business-state calculation. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01`
- `FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): generic draft FE adapter, obligation-detail FE adapter

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01.md`
- `frontend/src/modules/fees/pages/FeeDraftCreate.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-fee-draft-obligation.spec.ts`
- `artifacts/FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Reuse deep-module activity identity; the existing financial action must not append a duplicate activity.

## Verification Commands

- RED command: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-fee-draft-obligation.spec.ts --workers=1`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-fee-draft-obligation.spec.ts --workers=1`
- `cd frontend && npx eslint src/modules/fees/pages/FeeDraftCreate.vue --max-warnings 0`
- `git diff --check -- frontend/src/modules/fees/pages/FeeDraftCreate.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-fee-draft-obligation.spec.ts tasks/postdemo/v8/FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
