# FB3 Batch — Findings

## Backend Dependency Check
- Backend A3 Case Field Expansion: **CONFIRMED** in `backend/app/modules/cases/schemas.py`
- All 15 new fields present in CaseCreateIn (lines 42-59), CaseUpdateIn (lines 76-93), CaseOut (lines 126-143)

## Critical Issue: mapCase() Data Loss
- `cases.ts` has `BackendCase` interface + `mapCase()` that explicitly constructs output
- New 15 fields from backend response will be DROPPED by mapCase()
- `cases.ts` is NOT in FB3 allowlist
- **Resolution needed**: Either add cases.ts to allowlist or use spread operator workaround

## Bugs Found
(none yet)

## Deviations
- **cases.ts added to allowlist** (Option A approved by team lead): Required because mapCase() would drop all 15 new fields. Mechanical change (~30 lines), low risk. Without this, FB3 would be cosmetic-only.
