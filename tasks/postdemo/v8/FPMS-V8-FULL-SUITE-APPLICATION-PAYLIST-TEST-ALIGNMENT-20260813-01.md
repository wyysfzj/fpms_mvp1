# FPMS V8 Full-Suite Application PayList Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Align inherited application-fee PayList tests with reviewed obligation truth. The legacy
apply-fee generator still proves its exact reduced fee items, but its items have no reviewed
official-notice obligation lineage and therefore fail PayList creation with exact 409 and zero
official-payment writes. The zero-government-payment test uses the existing reviewed application
notice policy, explicit `PAY` instruction and canonical links before asserting the unchanged API
400 `GOV_PAYMENT_INVALID` boundary.

## RED and closure

Both inherited tests currently fail at PayList creation with 409
`PAY_LIST_OBLIGATION_LINK_REQUIRED` where they expect 200. Do not fabricate links for the legacy
draft. Preserve its exact 0.85-reduced fee facts and fail-closed no-write boundary. Move only the
generic zero-payment scenario onto existing reviewed application-notice test authority.

## Non-closure

No product/API/schema/migration/seed/rate/reduction/amount/Row283 change; no direct obligation or
link write, fallback, monkeypatch, skip, xfail or validation weakening. The authoritative policy
and service helpers remain unchanged and are verification inputs, not newly owned production facts.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-FULL-SUITE-APPLICATION-PAYLIST-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_apply_gov_paylist_readiness.py`
- `backend/tests/test_gov_paylist_validation_mvp.py`

## Verification

Run both inherited tests plus the authoritative application auto-draft policy suite; scoped Ruff,
format-check and exact diff-check. Independent High review requires P0/P1/P2 `0/0/0`.

## Current verification result

RED reproduced two exact 409 `PAY_LIST_OBLIGATION_LINK_REQUIRED` failures where inherited tests
expected 200. Final verification completes `32 passed` with four pre-existing warnings. Scoped
Ruff, format-check and exact diff-check pass. The legacy draft remains 0.85-reduced at exact
135/300/50 CNY; the zero-payment assertion now reaches the reviewed application-notice graph and
retains exact 400 `GOV_PAYMENT_INVALID`.
