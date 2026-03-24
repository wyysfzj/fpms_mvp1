# FB3 Batch — Task Plan

## Goal
Add the 15 new case fields (from backend A3) to CaseCreate, CaseEdit, and CaseDetail pages. Organize in collapsible sections.

## Backend Dependency
**Backend A3 (Case Field Expansion) — CONFIRMED COMPLETE**
All 15 fields present in `backend/app/modules/cases/schemas.py`: CaseCreateIn, CaseUpdateIn, CaseOut

## File Allowlist (STRICT)
| File | Action |
|------|--------|
| `frontend/src/api/cases.types.ts` | modify |
| `frontend/src/modules/cases/pages/CaseCreate.vue` | modify |
| `frontend/src/modules/cases/pages/CaseEdit.vue` | modify |
| `frontend/src/modules/cases/pages/CaseDetail.vue` | modify |

## Critical Finding
`cases.ts` has `mapCase()` that explicitly maps fields — 15 new fields will be DROPPED. `cases.ts` is NOT in allowlist. Architect must resolve.

## Status
- [ ] Architect Plan approved
- [ ] Implementation complete
- [ ] Quality Gate passed
- [ ] Review Report generated
