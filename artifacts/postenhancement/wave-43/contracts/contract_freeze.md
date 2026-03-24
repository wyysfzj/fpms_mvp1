# Wave 43 Contract Freeze

## Task Scope
- Wave: `43`
- Role: Architect / Designer
- Frozen tasks:
  - `tasks/postenhancement/frontend/PE-FE-AN-01.md`
  - `tasks/postenhancement/frontend/PE-FE-CL-01.md`
  - `tasks/postenhancement/frontend/PE-FE-COM-01.md`
- Scope intent: freeze API-client typing contracts for annuity/collections/commission with frontend conventions.

## Global Frontend API Conventions (Mandatory)
- Use existing HTTP/error stack only:
  - `frontend/src/api/http.ts`
  - `frontend/src/api/errors.ts`
  - `frontend/src/api/types.ts`
- API clients must:
  - use `http.get/post/put` with relative backend path (no host hardcode)
  - return typed `Promise<...>` values
  - reuse `Pagination<T>` for paged endpoints
  - keep backend wire keys in `snake_case` for query/body fields
  - define backend wire interfaces in `*.ts` (local `Backend*` types) and exported domain types in `*.types.ts`
- Error handling contract:
  - do not introduce custom interceptor stacks or per-client envelope formats
  - rely on normalized rejected `ApiError` from `http.ts` interceptor
  - preserve backend status semantics (`400/404/409/422` + auth `401/403`)

## Task Isolation / Allowlist Boundaries (Mandatory)
- `PE-FE-AN-01` may edit only:
  - `frontend/src/api/annuity.ts`
  - `frontend/src/api/annuity.types.ts`
- `PE-FE-CL-01` may edit only:
  - `frontend/src/api/collections.ts`
  - `frontend/src/api/collections.types.ts`
- `PE-FE-COM-01` may edit only:
  - `frontend/src/api/commission.ts`
  - `frontend/src/api/commission.types.ts`
- No cross-task shared-file edits:
  - do not modify `frontend/src/api/http.ts`, `frontend/src/api/types.ts`, shared stores, pages, router, or constants in these three tasks.

## PE-FE-AN-01 Freeze (Annuity API Client)

### Endpoint Coverage (Backend-aligned)
- `GET /annuity/tasks`
- `PUT /annuity/tasks/{task_id}/instruction`
- `POST /annuity/tasks/generate-drafts`

### Minimal Exported Types (`annuity.types.ts`)
- `AnnuityTask`
- `AnnuityTaskListParams`
- `AnnuityInstructionUpdatePayload`
- `AnnuityGenerateDraftsPayload`
- `AnnuityGenerateDraftResult` (summary + success[] + failed[])

### Minimal Function Signatures (`annuity.ts`)
1. `getAnnuityTasks(params?: AnnuityTaskListParams): Promise<Pagination<AnnuityTask>>`
2. `updateAnnuityTaskInstruction(taskId: number, payload: AnnuityInstructionUpdatePayload): Promise<AnnuityTask>`
3. `generateAnnuityDrafts(payload: AnnuityGenerateDraftsPayload): Promise<AnnuityGenerateDraftResult>`

### Mapping Rules
- Keep query keys as backend expects: `due_from`, `due_to`, `pending_mode`, `notice_status`, `page`, `page_size`.
- Keep generation payload keys backend-native: `task_ids`, `pay_next_year`, `currency`.
- Draft generation result must preserve per-item failure metadata (`code`, `message`, `status_code`) without lossy remap.
- Monetary values returned as decimal-like strings from backend may be normalized to `number` in domain model only if done consistently inside mapper.

### Status / Error Semantics
- Success: `200`
- Business errors: `400/404/409`
- Validation errors: `422`

## PE-FE-CL-01 Freeze (Collections API Client)

### Endpoint Coverage (Backend-aligned)
- `GET /dunning`
- `POST /dunning`
- `POST /bills/{bill_id}/bad-debt`
- `POST /bills/{bill_id}/bad-debt/restore`

### Minimal Exported Types (`collections.types.ts`)
- `DunningListParams`
- `DunningBatchListItem`
- `DunningGeneratePayload`
- `DunningGenerateResult` (summary + batches[])
- `BadDebtBillResult`

### Minimal Function Signatures (`collections.ts`)
1. `getDunning(params?: DunningListParams): Promise<Pagination<DunningBatchListItem>>`
2. `generateDunning(payload: DunningGeneratePayload): Promise<DunningGenerateResult>`
3. `markBillBadDebt(billId: string): Promise<BadDebtBillResult>`
4. `restoreBillBadDebt(billId: string): Promise<BadDebtBillResult>`

### Mapping Rules
- Preserve generate payload contract exactly:
  - required `to_date`
  - optional `client_id`, `client_ids`, `include_statuses`, `exclude_statuses`, `strict_conflict`
- Preserve generate response structure:
  - top-level `summary`
  - top-level `batches`
- Keep bad-debt responses mapped as bill snapshots (`id`, `bill_no`, `status`, `amount`, `balance`, etc.) without renaming that breaks page consumers.

### Status / Error Semantics
- `GET /dunning`: success `200`, invalid query `422` (and optional business `400`)
- `POST /dunning`: success `200`, business `400/404/409`, validation `422`
- bad-debt/restore: success `200`, business `400/404/409`, validation `422`

## PE-FE-COM-01 Freeze (Commission API Client)

### Endpoint Coverage (Backend-aligned)
- `GET /commission`
- `GET /commission/rules`
- `POST /commission/rules`
- `PUT /commission/rules/{rule_id}`
- `POST /commission/settlements`
- `POST /commission/settlements/{id}/generate-lines`
- `GET /commission/reports/settlement`

### Minimal Exported Types (`commission.types.ts`)
- `CommissionListParams`
- `CommissionRecord`
- `CommissionRule`
- `CommissionRuleCreatePayload`
- `CommissionRuleUpdatePayload`
- `CommissionSettlement`
- `CommissionSettlementCreatePayload`
- `CommissionSettlementGenerateLinesResult`
- `CommissionSettlementReportParams`
- `CommissionSettlementReportResult`

### Minimal Function Signatures (`commission.ts`)
1. `getCommission(params?: CommissionListParams): Promise<Pagination<CommissionRecord>>`
2. `getCommissionRules(params?: { enabled?: boolean; case_type?: string; fee_type?: string; q?: string; page?: number; page_size?: number }): Promise<Pagination<CommissionRule>>`
3. `createCommissionRule(payload: CommissionRuleCreatePayload): Promise<CommissionRule>`
4. `updateCommissionRule(ruleId: number, payload: CommissionRuleUpdatePayload): Promise<CommissionRule>`
5. `createCommissionSettlement(payload: CommissionSettlementCreatePayload): Promise<CommissionSettlement>`
6. `generateCommissionSettlementLines(id: number): Promise<CommissionSettlementGenerateLinesResult>`
7. `getCommissionSettlementReport(params?: CommissionSettlementReportParams): Promise<CommissionSettlementReportResult>`

### Mapping Rules
- Preserve backend filter names exactly (`settleable_date_from`, `settleable_date_to`, `created_at_from`, `created_at_to`, `time_field`, etc.).
- Use local mapper helpers for decimal/date fields where needed; keep transformation deterministic.
- Do not collapse report aggregate blocks; preserve backend report shape contract (aggregates + details dimensions).

### Status / Error Semantics
- Rule create: success `201`, business `400/409`, validation `422`
- Rule update: success `200`, business `400/404/409`, validation `422`
- Settlement create: success `201`, business `400/409`, validation `422`
- Generate-lines: success `200`, business `400/404/409`, validation `422`
- List/report endpoints: success `200`, business `400`, validation `422`

## Frontend Iron Rule Reminder
- All user-facing UI text must remain Simplified Chinese.
- This wave is API-layer only, so no UI text should be introduced.
- If unavoidable local fallback messages are added in API files, they must not be user-facing copy and must not introduce English UI prompt strings.

## Regression / Non-Regression Constraints
- No behavior drift in existing API clients outside allowlists.
- No global error-shape changes.
- No endpoint path invention; only frozen backend endpoints above.
- No cross-task coupling through shared helper edits.

## Acceptance Checklist
- [ ] Contract implementation for each task is confined to its own allowlisted files only.
- [ ] `annuity` client exposes frozen 3-function surface with typed request/response.
- [ ] `collections` client exposes frozen 4-function surface with typed request/response.
- [ ] `commission` client exposes frozen rule/record/settlement/report typed surface.
- [ ] All paginated endpoints use `Pagination<T>` and preserve `page/page_size/total`.
- [ ] Error semantics are preserved through existing normalized `ApiError` flow.
- [ ] No new UI text introduced in API layer; Simplified Chinese rule remains unviolated.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`
- [ ] Evidence artifacts generated for completion claim:
  - `artifacts/PE-FE-AN-01/**`
  - `artifacts/PE-FE-CL-01/**`
  - `artifacts/PE-FE-COM-01/**`
