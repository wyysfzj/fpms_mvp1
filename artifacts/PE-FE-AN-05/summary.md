# PE-FE-AN-05 Evidence Summary

## Executed Task
- Task ID: `PE-FE-AN-05`
- Task File: `tasks/postenhancement/frontend/PE-FE-AN-05.md`

## Scope Check
- Modified files:
  - `frontend/src/api/govPayments.ts` (new)
  - `frontend/src/api/govPayments.types.ts` (new)
  - `frontend/src/modules/annuity/pages/PayList.vue` (new)
  - `frontend/src/modules/annuity/pages/GovPaymentCreate.vue` (new)
- No other product files modified.

## Implemented
- 新增 govPayments typed API：
  - `createPayListFromFeeItems(payload)` -> `POST /pay-lists/from-fee-items`
  - `registerGovPayment(payload)` -> `POST /gov-payments`
- 新增中文错误映射与 422 字段错误映射，保持与现有 `http.ts` 归一化错误流一致。
- `PayList.vue`：支持费用项输入查询/生成、回执 summary/success/failed 展示、清单状态可见与缴费登记入口。
- `GovPaymentCreate.vue`：支持官方缴费登记提交，并展示返回的 `gov_payment` 与更新后的 `pay_list.status`。

## Verification Commands
- `cd frontend && npm run lint` -> `0`
- `cd frontend && npm run typecheck` -> `0`

## Expected Status Codes
- `POST /pay-lists/from-fee-items`: `200`, `400`, `404`, `401/403`, `422`（以及条目级 `failed[]` 可含 `409`）
- `POST /gov-payments`: `200`, `400`, `404`, `409`, `401/403`, `422`
