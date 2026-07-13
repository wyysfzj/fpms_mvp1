# FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `53`
Executor role: Frontend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `439`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: high
- `evidence_cost`: medium
- `chosen_runbook`: `P0-frontend-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-FE-ADAPTER`

- RED expectation: The row's exact `frontend/src/api/contracts/v8_*.contract.ts` import/shape probe makes serialized `FE-TYPE` fail before the named export/type exists.
- GREEN expectation: Contract probe, exact-file ESLint and serialized `FE-TYPE` pass without status/amount inference.

## Exact Closure Slice

Type evidence-version projection and one review action/result without inferring review/current/final state.

## Explicit Non-Closure

No page behavior, server-state inference or backend change. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-REVIEW-API-20260712-01`
- `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): review API, read projection

### Shared ownership serialization

- `frontend/src/api/documents.ts` order key `1`; project this order only across owners present in the active manifest.
- `frontend/src/api/documents.types.ts` order key `1`; project this order only across owners present in the active manifest.
- `FRONTEND_TYPECHECK_VERIFICATION` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01.md`
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/api/contracts/v8_document_evidence_review.contract.ts`
- `artifacts/FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd frontend && npm run typecheck`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd frontend && npm run typecheck`
- `cd frontend && npx eslint src/api/documents.ts src/api/documents.types.ts src/api/contracts/v8_document_evidence_review.contract.ts --max-warnings 0`
- `git diff --check -- frontend/src/api/documents.ts frontend/src/api/documents.types.ts frontend/src/api/contracts/v8_document_evidence_review.contract.ts tasks/postdemo/v8/FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
