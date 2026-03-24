# Batch FC4 — Progress Tracker

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| T1: Architect Plan | architect | DONE | Plan at 01_Architect_Plan.md |
| T2: billing.types.ts | frontend-impl | DONE | Added reversed_at + enriched CaseReceipt fields |
| T3: billing.ts | frontend-impl | DONE | BackendCaseReceipt + mapCaseReceipt + reversed_at + bill_id param |
| T4: BillDetail.vue offsets | frontend-impl | DONE | New "抵扣记录" tab, reverse button, fetchOffsets |
| T5: CaseReceiptsSummary.vue | frontend-impl | DONE | Enriched fields display with info-grid |
| T6: Quality Gate | frontend-impl | DONE | lint + typecheck + build all pass |
| T7: Review Report | reviewer | DONE | PASS — all criteria met, report at 04_Reviewer_Report.md |

## Key Decisions
- Offsets tab UI wired but uses stub (no backend list endpoint)
- CaseReceipt mapper bridges incompatible backend/frontend shapes
- Chinese labels inline (matching existing component patterns)
- `reversed_at` in types but will be undefined from backend (schema gap)

## Quality Gate Results
- [x] npm run lint — PASS
- [x] npm run typecheck — PASS
- [x] npm run build — PASS (3.31s)
