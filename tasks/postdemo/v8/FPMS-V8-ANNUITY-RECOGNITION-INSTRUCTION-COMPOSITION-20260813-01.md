# FPMS V8 Annuity Recognition / Instruction Composition

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Make the already-reviewed future-annuity recognition writer compose with the reviewed annuity
instruction adapter. A freshly recognized canonical obligation must accept one exact `PAY`
instruction and preserve its task/obligation/activity identities; the adapter must not require an
unrelated exception draft or accept the obsolete two-field recognition payload.

## Exact RED and closure

The new composition test calls `recognize_future_annuity_obligation` and then
`record_annuity_task_instruction` on the same persisted task. Recognition succeeds, but instruction
fails `404 ANNUITY_INSTRUCTION_LINK_NOT_FOUND` because its default validator still searches for an
obsolete exact two-field payload while the deep obligation service writes the canonical nested
payload.

This task may only make the instruction path use the existing canonical recognition validation and
align its focused test fixture to that same canonical payload. The underlying recognition,
instruction, draft, rate, reduction, evidence and transaction rules remain unchanged.

## Non-closure

- No API/UI, schema, migration, seed, rate/reduction policy, draft, PayList, payment or Row283 change.
- No legacy payload fallback, synthetic exception draft, direct result adoption, monkeypatch, skip,
  xfail, assertion deletion or relaxed error.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-ANNUITY-RECOGNITION-INSTRUCTION-COMPOSITION-20260813-01.md`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_annuity_instruction_obligation_adapter.py`

## Verification and acceptance

Run the exact instruction, recognition, draft-adapter and future-annuity auto-draft suites; run
scoped Ruff, format-check and exact diff-check. All tests must pass. Independent High review must
approve P0/P1/P2 `0/0/0` before inherited annuity alignment resumes.

## Current verification result

The exact four authoritative suites completed `101 passed` in `24.68s`, with two pre-existing
dependency warnings. Scoped Ruff passes. Whole-file format-check reports only three unrelated
pre-existing formatting regions outside this task's changed hunks (two future-annuity exception
lines in the shared service and one existing cross-case test expression); no formatter write or
unrelated churn is absorbed. Exact diff-check passes.
