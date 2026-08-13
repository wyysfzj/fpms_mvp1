# FPMS V8 Full-Suite OA Government PayList Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Align the inherited OA billing test with reviewed obligation truth. A legacy `OA_GOV` fee-draft
item without a canonical official source and obligation link must fail PayList creation with exact
409 `PAY_LIST_OBLIGATION_LINK_REQUIRED` and zero PayList/GovPayment writes. The same draft must
still support the existing client bill, payment, offset and case-receipt path for the full amount.

## RED and closure

The inherited positive PayList assertion fails because the reviewed adapter rejects the unlinked
legacy item with exact 409. Preserve that fail-closed result and prove zero official-payment writes;
do not fabricate an official source, obligation or link for the repository-local `OA_GOV` code.

## Non-closure

No product/API/schema/migration/seed/fee amount/bill/payment/offset/receipt/Row283 change; no direct
obligation/link write, fallback, monkeypatch, skip, xfail or assertion deletion. Application-fee
legacy cases remain outside this task.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-FULL-SUITE-OA-GOV-PAYLIST-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_b_oa_bill_payment_readiness.py`

## Verification

Run the inherited test plus the authoritative PayList activity adapter suite; scoped Ruff,
format-check and exact diff-check. Independent High review requires P0/P1/P2 `0/0/0`.

## Current verification result

RED reproduced the exact inherited failure: 409 `PAY_LIST_OBLIGATION_LINK_REQUIRED` where the
test expected 200. The final inherited plus authoritative adapter run completes `6 passed` with
four pre-existing dependency/deprecation warnings. Scoped Ruff, format-check and exact diff-check
pass. The inherited test continues through the unchanged 920 CNY bill/payment/offset/receipt path.
