# PE-FE-CL-01 Evidence Summary

- Task: `PE-FE-CL-01`
- Task file: `tasks/postenhancement/frontend/PE-FE-CL-01.md`
- Role: Frontend Developer
- Scope: collections API client (dunning, bad-debt, restore)

## Modified Product Files
- `frontend/src/api/collections.ts` (new)
- `frontend/src/api/collections.types.ts` (new)

## Contract/Implementation Notes
- Implemented frozen function surface:
  - `getDunning(params?)`
  - `generateDunning(payload)`
  - `markBillBadDebt(billId)`
  - `restoreBillBadDebt(billId)`
- Preserved backend snake_case query/body keys.
- Added backend-wire to domain mapping for decimal-like amount fields.
- Added collections-specific normalized error categorization helper (`mapCollectionsError`) based on existing `ApiError` flow.

## Verification
- `cd frontend && npm run lint` => PASS (`rc=0`)
- `cd frontend && npm run typecheck` => PASS (`rc=0`)

## Expected Endpoint Status Semantics (from frozen contract)
- `GET /dunning`: `200`, `400/422`, `401/403`
- `POST /dunning`: `200`, `400/404/409/422`, `401/403`
- `POST /bills/{bill_id}/bad-debt`: `200`, `400/404/409/422`, `401/403`
- `POST /bills/{bill_id}/bad-debt/restore`: `200`, `400/404/409/422`, `401/403`
