# FPMS-V8-LIVE-FIXTURE-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `17. Wave 8 — real paths and release close`
Catalog ordinal: `275`
Executor role: Tester / monitor

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `820`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: Contract/gate test fails on missing evidence or coverage.
- GREEN expectation: Exact audit/E2E/gate commands pass and any failure becomes a new task.

## Exact Closure Slice

Create dedicated live fixture with >100 activities, all lanes, gates/conflicts/unverified facts; do not modify shared P1 live seed.

## Explicit Non-Closure

No product fix, schema change or test-assertion weakening. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`
- `FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01`
- `FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01`
- `FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01`
- `FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01`
- `FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01`
- `FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): overlay UI

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LIVE-FIXTURE-20260712-01.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdV8OverlayLiveSeed.py`
- `backend/tests/test_v8_overlay_live_seed.py`
- `artifacts/FPMS-V8-LIVE-FIXTURE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Follow the frozen foundation/full close order; QA tasks report failures and never repair product code.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_overlay_live_seed.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_overlay_live_seed.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_overlay_live_seed.py && .venv/bin/ruff format tests/test_v8_overlay_live_seed.py && .venv/bin/ruff check tests/test_v8_overlay_live_seed.py`
- `git diff --check -- FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdV8OverlayLiveSeed.py backend/tests/test_v8_overlay_live_seed.py tasks/postdemo/v8/FPMS-V8-LIVE-FIXTURE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LIVE-FIXTURE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LIVE-FIXTURE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LIVE-FIXTURE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LIVE-FIXTURE-20260712-01` pass. Only then may this task be reported PASS.
