# FPMS-DEMO-V6-UI-PARITY-EMPTY-RECEIPT-SUMMARY-20260826-08T

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["api", "fee", "permission", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-EMPTY-RECEIPT-SUMMARY-20260826-08T.md
Chosen runbook: `P0-single-lane-story`

## Fixed References

- Approved design exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved implementation plan exact commit `80bd46829eaf5f798dda9422550a583c7fa12fde`.
- Accepted Task 08S HEAD `58cd1e7369d8f4f7dc96bfa8ca75346a08129bf9`.
- Reproducible strict Stage 01 RED: a fresh linked case performs
  `GET /api/v1/cases/{case_id}/receipts` and receives 404, producing a browser console error even
  though the normal UI treats the absence of billing data as an empty state.
- User approval: `` `批准 Task08T 新案件回款空摘要 200 最小整改边界，修复后恢复 Ordinal08` ``.
- Active Task 08 is paused at this exact console-error RED. Its disjoint uncommitted allowlist must
  remain byte-identical during Task 08T.

## Root Cause and Hypothesis

The existing aggregate receipt-summary GET represents a valid empty aggregate as a missing resource
when both receipt and bill rows are absent. For an existing case linked to a client with an explicit
`default_currency`, returning the same response envelope with zero totals and an empty bill list
will preserve authoritative currency and remove the erroneous 404 without hiding browser errors.

## Exact Closure Slice

Change only the existing case receipt-summary GET so an existing case linked to a client with an
explicit default currency and no bill/receipt rows returns a read-only zero summary with HTTP 200.

## Exact Behavior

1. `GET /cases/{case_id}/receipts` with `CaseReceipt.Read` returns the existing
   `CaseReceiptResponse` envelope when the case exists, its linked client supplies a non-empty
   `default_currency`, and no bill or receipt rows exist.
2. The empty response uses `id=case_id`, `case_id=case_id`, the exact client
   `default_currency`, `receivable_amt=0`, `received_amt=0`, `is_arrears=false`,
   `is_prepayment=false`, `is_commissionable=false`, and `bills=[]`; optional receipt facts remain
   null. The GET performs no write.
3. Missing cases and cases without an authoritative linked-client currency retain the existing 404
   behavior. Existing bill-only and receipt-backed summaries remain byte-semantically unchanged.
4. Existing route, response model, permission dependency, 401/403 behavior, frontend handling, and
   all billing mutation paths remain unchanged.
5. Focused public-API tests prove the empty 200 response uses a non-CNY client currency exactly,
   performs no writes, preserves missing-case 404, and keeps the existing bill-only summary green.

## Explicit Non-Closure

- No new endpoint, schema/model/migration/seed, frontend change, permission change, currency default
  or inference, receipt/bill creation, fee/amount rule, generic empty-summary abstraction, console
  filtering, retry, error swallowing, adjacent cleanup, or Stage 02–11 implementation.
- Do not modify any active Task 08 file or absorb its dirty baseline. Task 08 resumes only after 08T
  independent acceptance.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-EMPTY-RECEIPT-SUMMARY-20260826-08T.md`
- `backend/app/modules/billing/api.py`
- `backend/tests/test_case_receipt_empty_summary.py`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-EMPTY-RECEIPT-SUMMARY-20260826-08T/**`

## Verification Commands

```bash
(cd backend && PYTHONPATH=. \
  /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python -m pytest -q \
  tests/test_case_receipt_empty_summary.py tests/test_case_receipt_summary_bill_visibility.py)
(cd backend && /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python \
  -m ruff check app/modules/billing/api.py tests/test_case_receipt_empty_summary.py)
git diff --check
```

RED is the focused public GET returning 404 for an existing linked case with no billing rows. GREEN
is the exact empty response plus the existing bill-only regression passing. Do not run frontend,
broad backend, strict Playwright, or release gates in Task 08T.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-EMPTY-RECEIPT-SUMMARY-20260826-08T/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`, resume at Stage 01 after 08T acceptance.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`, remains deferred until after the demo.

## Done Definition

The fresh linked case returns an authoritative zero receipt summary without browser 404, focused
checks pass, active Task 08 bytes remain unchanged, and independent zero-finding review plus atomic
evidence accept the exact 08T range.

## Rollback

Run `git revert --no-edit <accepted-08T-range>`. Task 08 returns to its truthful Stage 01 console RED.
