# FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / CORRECTION REQUIRED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `72`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `458`
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

Copyable OA permits the frozen structured attachment combination only.

## Explicit Non-Closure

No second event/rate/policy, persistence adapter, endpoint, seed or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): evidence derivation

### Shared ownership serialization

- `backend/app/modules/documents/evidence_policy.py` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01.md`
- `backend/app/modules/documents/evidence_policy.py`
- `backend/tests/test_v8_oa_copyable_attachment_policy.py`
- `artifacts/FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_oa_copyable_attachment_policy.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_oa_copyable_attachment_policy.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_policy.py tests/test_v8_oa_copyable_attachment_policy.py && .venv/bin/ruff format app/modules/documents/evidence_policy.py tests/test_v8_oa_copyable_attachment_policy.py && .venv/bin/ruff check app/modules/documents/evidence_policy.py tests/test_v8_oa_copyable_attachment_policy.py`
- `git diff --check -- backend/app/modules/documents/evidence_policy.py backend/tests/test_v8_oa_copyable_attachment_policy.py tasks/postdemo/v8/FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority

- Authoritative contract: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, lines 423–441.
- Supplemental authority: row `20 / M4-E / H4-1` of `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk remains `HIGH`; `chosen_runbook: P0-prereq-heavy-story` supersedes the historical runbook above for Delta-4 execution.
- This appendix is latest-wins only for the corrected policy closure, prerequisites and serialization below. The rejected review, candidate patch, evidence and every other inherited byte remain immutable history, not acceptance authority.

### Exact corrected policy closure

- Correct only the existing public copyable-OA policy in `backend/app/modules/documents/evidence_policy.py`; its input is a frozen DTO carrying both typed evidence-version identity/hash and the exact manifest role/link.
- Discard the rejected candidate's ORM-role shortcut. Never infer typed evidence from `DocAttachment.official_file_role`, a filename, extension, display label or attachment order.
- Require exactly one `OA_STATEMENT_WORD` and exactly one `OA_MODIFIED_CLAIMS`.
- Permit at most one `OA_AMENDMENT_COMPARISON` and zero or more `OA_OTHER_PROOF` and `OA_ADDITIONAL_FILE` entries.
- Every supplied version must be `OA_STRUCTURED_ATTACHMENT`, current, independently `APPROVED`, and exactly linked by its same-case manifest.
- Duplicate evidence ID, duplicate manifest ID, cross-case/package identity, RAW or non-promoted evidence, hash/link/state/review mismatch, unknown role, missing required singleton or excess optional singleton fails closed.
- Do not select a candidate, collapse duplicates, trust an ORM role, reconstruct a missing link or infer a role from a filename.

### Dependencies and serialization

- D4-06 `FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01` must first reach independently accepted PASS.
- D4-07 `FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01` follows D4-06 and must reach independently accepted PASS.
- D4-08 `FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01` follows D4-07 and must reach independently accepted PASS before this correction starts.
- Document-chain ownership is strict D4-06 → D4-07 → D4-08 → row 20 / Task 72 → row 21 / Task 73. Each owner releases shared verification only after independent acceptance; no shared edit or verification runs concurrently.
- Row 21 may consume only this corrected manifest/version policy after row 20 independently passes; it must not bypass the policy or infer typed evidence itself.

### Explicit non-closure

- Keep the existing Allowed Files list exact; add no source, test, task, manifest or artifact path.
- Do not implement or alter D4-06, D4-07, D4-08, promotion/derivation/registration behavior, Task 73's DRAFT OA reply seam, external submission, lifecycle, API/router/schema/model/migration/seed/UI or customer policy.
- This Ultra materialization performs no product/test edit, candidate-patch rewrite, rejected-evidence rewrite or evidence initialization and runs only the repository atomic task check.
