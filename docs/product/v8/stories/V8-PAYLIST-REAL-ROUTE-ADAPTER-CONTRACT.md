# Story Contract V8-PAYLIST-REAL-ROUTE-ADAPTER

- Risk: `PROTECTED`
- Trigger: the row 277 real-UI E2E reached two missing router adapters after all row
  159–164 services and projections were current-verified.
- Outcome: the existing PayList create and export HTTP routes durably expose the accepted
  caller-owned transaction and internal-export services without collapsing internal export,
  official workbook, payment, or official evidence facts.
- Authority: `docs/product/v8/domain-contract.md`, frozen catalog rows 157 and 159–164,
  `V8-PAYLIST-INTERNAL-EXPORT-SERVICE`,
  `V8-PAYLIST-EXPORT-BOUNDARY-CURRENT-ADOPTION`, and the row 277 exact E2E contract.

## Exact observable contract

1. `POST /api/v1/pay-lists/from-fee-items` keeps its request, permission, status and direct
   response shape. It supplies the authenticated user ID as `actor_id`, invokes the accepted
   `create_pay_list_from_fee_items` service once, commits once before returning success, and
   rolls back on any service or commit failure. A returned PayList ID must be durable for the
   immediately following read.
2. `POST /api/v1/pay-lists/{pay_list_id}/export` keeps its bodyless request, permission,
   binary `200` response, media type and attachment filename semantics. Missing PayLists stay
   `404 PAY_LIST_NOT_FOUND`; non-`DRAFT` PayLists stay `409 PAY_LIST_STATE_CONFLICT`.
3. The export route calls only `export_internal_pay_list` with the authenticated actor and
   deterministic PayList-scoped key
   `pay-list-internal-export:http-v1:{pay_list_id}`. This makes transport retry an exact
   replay because the existing HTTP request has no caller-provided idempotency carrier.
4. A fresh export commits the artifact and activity transaction once before returning bytes.
   A service failure rolls back. A commit failure rolls back and compensates only a newly
   written managed file; replayed durable files are never deleted by request rollback.
5. Internal export leaves the PayList header status unchanged. It creates/reuses exactly one
   `INTERNAL_XLSX` fact for this route key and never creates or infers an official workbook,
   `OFFICIAL_XLSM` evidence, payment acceptance, receipt, or legal/lifecycle transition.

## Exact paths and verification

- `backend/app/modules/annuity/api.py`
- `backend/tests/test_v8_pay_list_real_route_adapter.py`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-pay-list-boundary-live.spec.ts`
- this contract

Required verification is the focused backend adapter test, accepted rows 157 and 159–164
regressions, scoped Ruff/diff checks, and the exact row 277 live Playwright test against a
fresh migrated and seeded SQLite database. SQLite-writing verification is serialized.

## Non-goals and rollback

No service-rule change, schema/migration, official workbook generation or upload, payment
registration or receipt fabrication, PayList header redesign, UI redesign, new request
field/header, customer decision, unrelated route, broad cleanup, or reinterpretation of an
accepted catalog row. Rollback reverts this adapter story; accepted deep services remain.
