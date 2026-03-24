# PE-FE-CM-03

Status: PASS

Scope:
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/modules/cases/pages/CaseCreate.vue`
- `frontend/src/modules/cases/pages/CaseEdit.vue`
- `frontend/src/modules/cases/pages/CaseDetail.vue`

Changes:
- extended case API/types to map foreign-agent, bio-deposit, PCT, and invalidation fields
- added create/edit sections for foreign-agent select + quick-create, bio-deposit rows, PCT fields, and invalidation fields
- added front-end validation matching deferred Batch 1 rules
- added detail-page display for all deferred Batch 1 case fields

Validation:
- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
