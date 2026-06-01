# PD-P1-FE-API-CONTRACTS-01 — Frontend API contracts for P1 official workflows

## Exact Closure Slice

Add frontend API clients and TypeScript types for P1 official fields, attachment manifest roles, filing package, OA package, receipt archive, fee linkage, and letter handoff backend contracts.

## Explicit Non-Closure

No Vue page behavior. No router/menu changes. No backend code. No UI redesign.

## Remaining Follow-Up Task IDs

- `PD-P1-FE-CASE-OFFICIAL-FIELDS-01`
- `PD-P1-FE-ATTACHMENT-GATES-01`
- `PD-P1-FE-FILING-PREP-01`
- `PD-P1-FE-OA-PACKAGE-01`
- `PD-P1-FE-RECEIPT-ARCHIVE-01`
- `PD-P1-FE-FEE-LINKAGE-01`
- `PD-P1-FE-LETTER-HANDOFF-01`

## Allowed Files

- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/api/fees.ts`
- `frontend/src/api/fees.types.ts`
- `frontend/src/api/officialWorkflows.ts`
- `frontend/src/api/officialWorkflows.types.ts`
- `tasks/postdemo/PD-P1-FE-API-CONTRACTS-01.md`
- `artifacts/PD-P1-FE-API-CONTRACTS-01/**`

## Verification Commands

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- `./scripts/task_validate.sh PD-P1-FE-API-CONTRACTS-01`

## Evidence Path

- `artifacts/PD-P1-FE-API-CONTRACTS-01/`

## Acceptance

- Type exports cover all backend P1 package/read/update responses.
- API clients do not introduce page-level behavior or hardcoded mock data.
- Existing callers continue to compile.
