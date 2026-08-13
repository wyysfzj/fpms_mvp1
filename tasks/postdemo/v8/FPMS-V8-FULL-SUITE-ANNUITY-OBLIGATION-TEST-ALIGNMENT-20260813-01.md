# FPMS V8 Full-Suite Annuity Obligation Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Align inherited annuity draft/PayList tests with reviewed obligation truth. Each positive target
first receives a current official rate, same-case confirmed grant evidence, canonical recognition
and `PAY` instruction through the approved services. Negative cases remain unseeded.

## RED and closure

Fifteen positive inherited tests fail `ANNUITY_OBLIGATION_LINK_REQUIRED`. Test-only setup must call
the real recognition and instruction seams; it must not directly write obligation/activity/lineage
carriers. The reviewed draft adapter leaves legacy `draft_generated` false and emits the official
`CN_ANNUITY_FEE_INV` code, so inherited assertions align to those exact facts.

## Non-closure

No product/API/UI/schema/migration/seed/rate/reduction/PayList/payment/Row283 change; no fallback,
legacy payload, monkeypatch, skip, xfail, negative-test lineage or assertion deletion. Separate
application/OA legacy fee links remain outside this task.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-FULL-SUITE-ANNUITY-OBLIGATION-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/v8_annuity_obligation_test_support.py`
- `backend/tests/test_annuity_generate.py`
- `backend/tests/test_annuity_e2e.py`

## Verification

Run both inherited files plus authoritative recognition, instruction and draft-adapter suites;
scoped Ruff and exact diff-check. Independent High review requires P0/P1/P2 `0/0/0`.

## Current verification result

The two inherited files complete `42 passed` (`13 + 29`) with four pre-existing warnings per
file-run. The exact three authoritative suites complete `79 passed` with two pre-existing
dependency warnings. Scoped Ruff and exact diff-check pass. The aligned assertions preserve the
reviewed facts exposed after lineage became reachable: official fee code/amount, reused draft
identity, CNY-only obligation scope, payment/export decoupling and idempotent internal export.
