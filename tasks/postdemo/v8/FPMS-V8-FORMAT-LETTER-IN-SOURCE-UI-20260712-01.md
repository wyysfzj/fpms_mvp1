# FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `92`
Executor role: Frontend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `497`
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

Existing handoff panel exposes the Chinese format-letter action on eligible IN source, not arbitrary OUT, and displays the actual archived version/hash.

## Explicit Non-Closure

No backend change, second page capability or frontend business-state calculation. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `backend/tests/test_pd_p1_letter_handoff_api.py`: Exact read-only pre-V8 regression required by the approved dependency alias.
- `inherited` — `PD-P1-BE-LETTER-HANDOFF-API-01`: Accepted task file tasks/postdemo/PD-P1-BE-LETTER-HANDOFF-API-01.md; PASS evidence artifacts/PD-P1-BE-LETTER-HANDOFF-API-01/summary.md, artifacts/PD-P1-BE-LETTER-HANDOFF-API-01/results.jsonl and artifacts/PD-P1-BE-LETTER-HANDOFF-API-01/git/diff.patch; targeted test backend/tests/test_pd_p1_letter_handoff_api.py.

- Approved source dependency cell (verbatim): archive API behavior

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01.md`
- `frontend/src/modules/officialWorkflows/components/LetterHandoffPanel.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-format-letter-in-source-ui.spec.ts`
- `artifacts/FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-format-letter-in-source-ui.spec.ts --workers=1`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_pd_p1_letter_handoff_api.py`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-format-letter-in-source-ui.spec.ts --workers=1`
- `cd frontend && npx eslint src/modules/officialWorkflows/components/LetterHandoffPanel.vue --max-warnings 0`
- `git diff --check -- frontend/src/modules/officialWorkflows/components/LetterHandoffPanel.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-format-letter-in-source-ui.spec.ts tasks/postdemo/v8/FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01` pass. Only then may this task be reported PASS.
