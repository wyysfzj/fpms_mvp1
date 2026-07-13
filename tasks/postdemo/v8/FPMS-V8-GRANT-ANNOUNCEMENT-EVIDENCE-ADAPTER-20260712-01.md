# FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `205`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `713`
- Expected manifest phase: `deferred`
- Customer gate requirement: `DG-GRANT-EVIDENCE-SOURCE[GLOBAL], DG-GRANT-MANUAL-REVIEW[GLOBAL]`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: Exact adapter test proves the old direct write/missing activity/premature state.
- GREEN expectation: Exact adapter test plus listed inherited regressions pass; only the named entrypoint changes.

## Exact Closure Slice

Map one already accepted controlled announcement candidate to the announcement lifecycle event exactly once; no review-state mutation or direct status write.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01`
- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-REVIEW-SERVICE-20260712-01`
- `FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01`

### External, gate and inherited prerequisites

- `gate` — `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `gate` — `DG-GRANT-MANUAL-REVIEW:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.
- `external` — `backend/tests/test_v8_direct_case_status_write_gate.py`: Foundation direct-status static-gate regression; rerun after this adapter's targeted test without editing it.

- Approved source dependency cell (verbatim): review service, announcement rule, direct-status static gate

### Shared ownership serialization

- `backend/app/modules/documents/evidence_policy.py` order key `5`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01.md`
- `backend/app/modules/documents/evidence_policy.py`
- `backend/tests/test_v8_grant_announcement_evidence_adapter.py`
- `artifacts/FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Require the exact persisted gate and lane activation; absent/revoked/future/scope-mismatched decisions are 409/no write.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_announcement_evidence_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_grant_announcement_evidence_adapter.py tests/test_v8_direct_case_status_write_gate.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_policy.py tests/test_v8_grant_announcement_evidence_adapter.py && .venv/bin/ruff format app/modules/documents/evidence_policy.py tests/test_v8_grant_announcement_evidence_adapter.py && .venv/bin/ruff check app/modules/documents/evidence_policy.py tests/test_v8_grant_announcement_evidence_adapter.py`
- `git diff --check -- backend/app/modules/documents/evidence_policy.py backend/tests/test_v8_grant_announcement_evidence_adapter.py tasks/postdemo/v8/FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
