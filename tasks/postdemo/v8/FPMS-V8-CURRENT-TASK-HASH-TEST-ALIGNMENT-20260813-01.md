# FPMS V8 Current Task-Hash Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`
Runbook: `P0-single-lane-story`

## Observable outcome

Align the four exact historical task-card/hash tests exposed by the Row281 Full backend matrix
with reviewed append-only latest-wins task bytes. The tests must retain approved baseline hashes,
prove current append-only structure and bind the current task-card hashes without weakening
dependency order or source/configuration fail-closed semantics.

## Exact closure

- Update only stale approved task-card hash/baseline expectations.
- Preserve exact ordered members, prerequisites, atomic owners, append-only proof and
  `CONFIG_REQUIRED / PENDING / 409 NO WRITE` assertions.
- Add no acceptance of arbitrary task-card drift.

## Non-closure

No task-card, product, source decision, schema, migration or ledger change; no Row281 adoption.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-CURRENT-TASK-HASH-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_v8_grant_review_gate_manifest_contract.py`
- `backend/tests/test_v8_grant_source_gate_manifest_contract.py`
- `backend/tests/test_v8_input_activation_decoupling_contract.py`

`backend/uv.lock` remains unrelated and untouched.

## Verification

Run the exact four failing tests from the Row281 result, scoped Ruff, exact diff check, then obtain
independent High review. This task changes tests only and cannot claim Row281 or production PASS.
