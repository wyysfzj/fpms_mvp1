# FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `10. Wave 2B — one lifecycle event per task`
Catalog ordinal: `28`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `393`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-RULE`

- RED expectation: Exact public rule test fails on the named transition/calculation.
- GREEN expectation: Exact rule test passes every named success/boundary/fail-closed case.

## Exact Closure Slice

OA notice enters OA response with `oa_sequence`; legal status unchanged.

## Explicit Non-Closure

No second event/rate/policy, persistence adapter, endpoint, seed or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
- `FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): [DEFAULT LIFECYCLE SEAM]

### Shared ownership serialization

- `backend/app/modules/cases/lifecycle_rules.py` order key `11`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01.md`
- `backend/tests/test_v8_lifecycle_oa_notice.py`
- `backend/app/modules/cases/lifecycle_rules.py`
- `artifacts/FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Modify only lifecycle_rules.py plus the exact test, depend on apply_lifecycle_event(), preserve strict table order and implement exactly one event.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_oa_notice.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_oa_notice.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_oa_notice.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_oa_notice.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_oa_notice.py app/modules/cases/lifecycle_rules.py`
- `git diff --check -- backend/tests/test_v8_lifecycle_oa_notice.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01` pass. Only then may this task be reported PASS.
