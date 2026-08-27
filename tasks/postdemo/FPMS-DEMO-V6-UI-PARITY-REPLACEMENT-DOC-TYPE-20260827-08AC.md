# FPMS-DEMO-V6-UI-PARITY-REPLACEMENT-DOC-TYPE-20260827-08AC

Risk: HIGH
Closure-Tags: api, lifecycle, lineage
Runbook: P0-single-lane-story
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-REPLACEMENT-DOC-TYPE-20260827-08AC.md

## Design references

- User approval: `` `批准 Task08AC 更正授权通知官方来文类型最小投影边界` ``.
- Accepted Task08AB HEAD `354b987b00d239b4cee46276d49326191a1be4e0`.
- Latest strict UI Stage 07 diagnostic: the replacement notice has executable
  `GRANT_NOTICE` template semantics, incoming direction, reviewed evidence, and one valid
  archived lifecycle activity, but its persisted `doc_type` is null.

## Exact Closure Slice

For `POST /grant-fee-tasks/{task_id}/replacement-notice`, persist the route-owned replacement
document type as `OFFICIAL_IN` when constructing the existing `DocumentCreateIn`. Prove through
the focused public API test that the normal omitted-input request returns and persists
`doc_type=OFFICIAL_IN`, including the existing idempotent replay.

## Scope decision — FIXED

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: backend-only route projection
- `evidence_cost`: low
- `chosen_runbook`: `P0-single-lane-story`
- The replacement-notice route already fixes `case_id` and `direction`; `doc_type=OFFICIAL_IN`
  is the same route-owned projection, not a new customer or source fact.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-REPLACEMENT-DOC-TYPE-20260827-08AC.md`
- `backend/app/modules/grant_fees/api.py`
- `backend/tests/test_addgap_grant_replacement_api.py`

## Explicit Non-Closure

- No frontend, schema, migration, seed, backfill, document-template, lifecycle-transition,
  evidence-review, fee/rate/amount, preview, confirmation, permission, or response-envelope change.
- No relaxation of the Stage 07 preview or evidence-lineage guards.
- No broad backend suite, broad Playwright, Stage 08+, runbook/docs, candidate, or release work.
- Do not absorb or modify active Task08 dirty files.

## Verification Commands

1. Focused RED then GREEN:
   `cd backend && PYTHONPATH=. .venv/bin/pytest -q tests/test_addgap_grant_replacement_api.py::test_replacement_notice_api_returns_explicit_composite_and_stable_200_retry`.
2. Focused file GREEN:
   `cd backend && PYTHONPATH=. .venv/bin/pytest -q tests/test_addgap_grant_replacement_api.py`.
3. Scoped Ruff check for the two Python files.
4. Exact baseline-subtracted scope and `git diff --check`.
5. Independent findings-only review with `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`.
6. Atomic evidence validation after review.

## Evidence Path

`artifacts/FPMS-DEMO-V6-UI-PARITY-REPLACEMENT-DOC-TYPE-20260827-08AC/`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`

## Prompt

Implement only the fixed route-owned document-type projection. Do not add optional behavior or
absorb any follow-up.
