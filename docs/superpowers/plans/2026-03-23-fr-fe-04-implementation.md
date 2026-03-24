# FR-FE-04 官费清单与缴费 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不违反 Phase 3 无 schema 变更约束的前提下，交付 `FR-FE-04` 的 Phase 3 兼容闭环，并把 schema 受限部分明确拆成阻塞 follow-up。

**Architecture:** 后端统一收敛到 `backend/app/modules/annuity/api.py` 与 `backend/app/modules/annuity/service.py`，复用现有 `T_PayList/T_GovPayment` 模型与已有残留 endpoint，再补齐历史清单、查询、详情、导出、缴费完成和手工补录切片。前端以“费用管理 → 官费清单”为产品语义，底层可复用现有 annuity 页面与 API 文件，但必须把共享所有权文件串行化。

**Tech Stack:** FastAPI, SQLAlchemy ORM, Pytest, Vue 3, Element Plus, TypeScript, Ruff

---

## File Structure Lock

### Backend shared ownership

- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_annuity_e2e.py`
- `backend/app/modules/annuity/export_excel.py` (new, if export task needs helper)

### Frontend shared ownership

- `frontend/src/router/index.ts`
- `frontend/src/constants/menu.ts`
- `frontend/src/api/govPayments.ts`
- `frontend/src/api/govPayments.types.ts`
- `frontend/src/modules/annuity/pages/PayList.vue`
- `frontend/src/modules/annuity/pages/GovPaymentCreate.vue`
- `frontend/src/modules/annuity/pages/PayListDetail.vue` (new)
- `frontend/src/modules/annuity/components/ManualGovPaymentDialog.vue` (new)

### Task document root

- `tasks/fr-fe-04/`
- `tasks/fr-fe-04/blocked/`

## Atomic Task Inventory

Executable task docs:

- `tasks/fr-fe-04/FRFE04-BE-00.md`
- `tasks/fr-fe-04/FRFE04-BE-01.md`
- `tasks/fr-fe-04/FRFE04-BE-RBAC-01.md`
- `tasks/fr-fe-04/FRFE04-BE-02.md`
- `tasks/fr-fe-04/FRFE04-BE-03.md`
- `tasks/fr-fe-04/FRFE04-BE-RBAC-02.md`
- `tasks/fr-fe-04/FRFE04-BE-04.md`
- `tasks/fr-fe-04/FRFE04-BE-05.md`
- `tasks/fr-fe-04/FRFE04-BE-06.md`
- `tasks/fr-fe-04/FRFE04-BE-07.md`
- `tasks/fr-fe-04/FRFE04-FE-01.md`
- `tasks/fr-fe-04/FRFE04-FE-02.md`
- `tasks/fr-fe-04/FRFE04-FE-03.md`
- `tasks/fr-fe-04/FRFE04-FE-04.md`
- `tasks/fr-fe-04/FRFE04-FE-05.md`
- `tasks/fr-fe-04/FRFE04-QA-01.md`

Blocked follow-up docs:

- `tasks/fr-fe-04/blocked/FRFE04-BLOCK-01.md`
- `tasks/fr-fe-04/blocked/FRFE04-BLOCK-02.md`
- `tasks/fr-fe-04/blocked/FRFE04-BLOCK-03.md`
- `tasks/fr-fe-04/blocked/FRFE04-BLOCK-04.md`
- `tasks/fr-fe-04/blocked/FRFE04-BLOCK-05.md`

## Execution Waves

Wave 1:
- `FRFE04-BE-00`
- Mode: serialized, sole backend owner of `annuity/api.py`, `annuity/service.py`, `test_annuity_e2e.py`

Wave 2:
- `FRFE04-BE-01`
- Mode: serialized, sole backend owner of `annuity/api.py`, `annuity/service.py`, `test_annuity_e2e.py`

Wave 3:
- `FRFE04-BE-RBAC-01`
- Mode: serialized, sole backend owner of `rbac/service.py`, `docs/README.md`, `docs/02_permissions_rbac.md`, and `docs/permissions_matrix.md`

Wave 4:
- `FRFE04-BE-02`
- Mode: serialized, sole backend owner of `annuity/api.py`, `annuity/service.py`, `test_annuity_e2e.py`

Wave 5:
- `FRFE04-BE-03`
- Mode: serialized, sole backend owner of `annuity/api.py`, `annuity/service.py`, `test_annuity_e2e.py`

Wave 6:
- `FRFE04-BE-RBAC-02`
- Mode: serialized, sole backend owner of `rbac/service.py`, `docs/README.md`, `docs/02_permissions_rbac.md`, and `docs/permissions_matrix.md`

Wave 7:
- `FRFE04-BE-04`
- Mode: serialized, sole backend owner of `annuity/api.py`, `annuity/service.py`, `annuity/export_excel.py`, `test_annuity_e2e.py`

Wave 8:
- `FRFE04-BE-STATE-01`
- Mode: serialized, sole backend owner of `annuity/service.py`, `test_annuity_e2e.py`

Wave 9:
- `FRFE04-BE-05`
- Mode: serialized, sole backend owner of `annuity/api.py`, `annuity/service.py`, `test_annuity_e2e.py`

Wave 10:
- `FRFE04-BE-06`
- Mode: serialized, sole backend owner of `annuity/api.py`, `annuity/service.py`, `test_annuity_e2e.py`

Wave 11:
- `FRFE04-BE-07`
- Mode: serialized, sole backend owner of `annuity/api.py`, `annuity/service.py`, `test_annuity_e2e.py`

Wave 12:
- `FRFE04-FE-01`
- Mode: serialized, sole frontend owner of `menu.ts`, `router/index.ts`, `api/govPayments*`

Wave 13:
- `FRFE04-FE-02`
- Mode: serialized, sole frontend owner of `PayList.vue`, `api/govPayments*`

Wave 13:
- `FRFE04-FE-03`
- Mode: serialized, sole frontend owner of `PayListDetail.vue`, `router/index.ts`, `api/govPayments*`

Wave 14:
- `FRFE04-FE-04`
- Mode: serialized, sole frontend owner of `GovPaymentCreate.vue`, `api/govPayments*`

Wave 15:
- `FRFE04-FE-05`
- Mode: serialized, sole frontend owner of `ManualGovPaymentDialog.vue`, `PayListDetail.vue`, `api/govPayments*`

Wave 16:
- `FRFE04-QA-01`
- Mode: serialized, monitor-only final audit after all executable implementation tasks pass

Blocked ledger:
- `FRFE04-BLOCK-01` .. `FRFE04-BLOCK-05`

## Task Steps

### Task 1: `FRFE04-BE-00` Existing generation endpoint hardening

**Files:**
- Modify: `backend/app/modules/annuity/api.py`
- Modify: `backend/app/modules/annuity/service.py`
- Test: `backend/tests/test_annuity_e2e.py`
- Spec: `tasks/fr-fe-04/FRFE04-BE-00.md`

- [ ] Read the existing endpoint and current failing/partial behavior against the spec doc.
- [ ] Add or update a focused failing pytest for `POST /pay-lists/from-fee-items`.
- [ ] Run `cd backend && pytest -q backend/tests/test_annuity_e2e.py -k pay_list_from_fee_items`.
- [ ] Implement the minimal changes needed for the exact closure slice only.
- [ ] Run task-scoped Ruff and pytest:
  - `cd backend && ruff check --fix app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
  - `cd backend && ruff format app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
  - `cd backend && ruff check app/modules/annuity/api.py app/modules/annuity/service.py tests/test_annuity_e2e.py`
  - `cd backend && pytest -q tests/test_annuity_e2e.py -k pay_list_from_fee_items`
- [ ] Generate `artifacts/FRFE04-BE-00/**`.
- [ ] Commit only task-allowlist changes.

### Task 2: `FRFE04-BE-01` Historical pay-list header creation

**Files:**
- Modify: `backend/app/modules/annuity/api.py`
- Modify: `backend/app/modules/annuity/service.py`
- Test: `backend/tests/test_annuity_e2e.py`
- Spec: `tasks/fr-fe-04/FRFE04-BE-01.md`

- [ ] Write a failing pytest for `POST /pay-lists`.
- [ ] Run `cd backend && pytest -q tests/test_annuity_e2e.py -k historical_pay_list_create`.
- [ ] Implement the minimal endpoint/service slice.
- [ ] Run task-scoped Ruff and pytest.
- [ ] Generate `artifacts/FRFE04-BE-01/**`.
- [ ] Commit only task-allowlist changes.

### Task 3: `FRFE04-BE-02` Pay-list query

**Files:**
- Modify: `backend/app/modules/annuity/api.py`
- Modify: `backend/app/modules/annuity/service.py`
- Test: `backend/tests/test_annuity_e2e.py`
- Spec: `tasks/fr-fe-04/FRFE04-BE-02.md`

- [ ] Write a failing pytest for `GET /pay-lists` with supported filters only.
- [ ] Run `cd backend && pytest -q tests/test_annuity_e2e.py -k pay_list_query`.
- [ ] Implement the minimal endpoint/service slice.
- [ ] Run task-scoped Ruff and pytest.
- [ ] Generate `artifacts/FRFE04-BE-02/**`.
- [ ] Commit only task-allowlist changes.

### Task 3A: `FRFE04-BE-RBAC-01` PayList.Read permission registration

**Files:**
- Modify: `backend/app/modules/rbac/service.py`
- Modify: `docs/README.md`
- Modify: `docs/02_permissions_rbac.md`
- Modify: `docs/permissions_matrix.md`
- Spec: `tasks/fr-fe-04/FRFE04-BE-RBAC-01.md`

- [ ] Add `PayList.Read` to seeded role permissions where this story requires list/detail read access.
- [ ] Align the authoritative RBAC docs so the new read permission and endpoint matrix are documented without stale pointers.
- [ ] Add `GET /pay-lists` and later `GET /pay-lists/{id}` to the permissions matrix with `PayList.Read`.
- [ ] Verify no unrelated permission codes are changed.
- [ ] Record task-scoped evidence under `artifacts/FRFE04-BE-RBAC-01/**`.
- [ ] Commit only task-allowlist changes.

### Task 3B: `FRFE04-BE-RBAC-02` PayList.Export permission registration

**Files:**
- Modify: `backend/app/modules/rbac/service.py`
- Modify: `docs/README.md`
- Modify: `docs/02_permissions_rbac.md`
- Modify: `docs/permissions_matrix.md`
- Spec: `tasks/fr-fe-04/FRFE04-BE-RBAC-02.md`

- [ ] Add `PayList.Export` to seeded role permissions where this story requires export access.
- [ ] Align the authoritative RBAC docs so the new export permission and endpoint matrix are documented without stale pointers.
- [ ] Add `POST /pay-lists/{id}/export` to the permissions matrix with `PayList.Export`.
- [ ] Verify no unrelated permission codes are changed.
- [ ] Record task-scoped evidence under `artifacts/FRFE04-BE-RBAC-02/**`.
- [ ] Commit only task-allowlist changes.

### Task 4: `FRFE04-BE-03` Pay-list detail

**Files:**
- Modify: `backend/app/modules/annuity/api.py`
- Modify: `backend/app/modules/annuity/service.py`
- Test: `backend/tests/test_annuity_e2e.py`
- Spec: `tasks/fr-fe-04/FRFE04-BE-03.md`

- [ ] Write a failing pytest for `GET /pay-lists/{id}`.
- [ ] Run `cd backend && pytest -q tests/test_annuity_e2e.py -k pay_list_detail`.
- [ ] Implement the minimal endpoint/service slice.
- [ ] Run task-scoped Ruff and pytest.
- [ ] Generate `artifacts/FRFE04-BE-03/**`.
- [ ] Commit only task-allowlist changes.

### Task 5: `FRFE04-BE-04` Export to Excel

**Files:**
- Modify: `backend/app/modules/annuity/api.py`
- Modify: `backend/app/modules/annuity/service.py`
- Create: `backend/app/modules/annuity/export_excel.py`
- Test: `backend/tests/test_annuity_e2e.py`
- Spec: `tasks/fr-fe-04/FRFE04-BE-04.md`

- [ ] Write a failing pytest for `POST /pay-lists/{id}/export`.
- [ ] Run `cd backend && pytest -q tests/test_annuity_e2e.py -k pay_list_export`.
- [ ] Implement minimal Excel generation and `DRAFT -> EXPORTED` rule.
- [ ] Run task-scoped Ruff and pytest.
- [ ] Generate `artifacts/FRFE04-BE-04/**`.
- [ ] Commit only task-allowlist changes.

### Task 6: `FRFE04-BE-05` Mark pay list paid

**Files:**
- Modify: `backend/app/modules/annuity/api.py`
- Modify: `backend/app/modules/annuity/service.py`
- Test: `backend/tests/test_annuity_e2e.py`
- Spec: `tasks/fr-fe-04/FRFE04-BE-05.md`

- [ ] Write a failing pytest for `POST /pay-lists/{id}/mark-paid`.
- [ ] Run `cd backend && pytest -q tests/test_annuity_e2e.py -k pay_list_mark_paid`.
- [ ] Implement minimal transition logic requiring prior `EXPORTED`.
- [ ] Run task-scoped Ruff and pytest.
- [ ] Generate `artifacts/FRFE04-BE-05/**`.
- [ ] Commit only task-allowlist changes.

### Task 7: `FRFE04-BE-06` Existing gov-payment registration hardening

**Files:**
- Modify: `backend/app/modules/annuity/api.py`
- Modify: `backend/app/modules/annuity/service.py`
- Test: `backend/tests/test_annuity_e2e.py`
- Spec: `tasks/fr-fe-04/FRFE04-BE-06.md`

- [ ] Write a failing pytest for `POST /gov-payments` generated-row registration.
- [ ] Run `cd backend && pytest -q tests/test_annuity_e2e.py -k gov_payment_register`.
- [ ] Implement the minimal endpoint/service slice.
- [ ] Run task-scoped Ruff and pytest.
- [ ] Generate `artifacts/FRFE04-BE-06/**`.
- [ ] Commit only task-allowlist changes.

### Task 8: `FRFE04-BE-07` Manual gov-payment row under existing pay list

**Files:**
- Modify: `backend/app/modules/annuity/api.py`
- Modify: `backend/app/modules/annuity/service.py`
- Test: `backend/tests/test_annuity_e2e.py`
- Spec: `tasks/fr-fe-04/FRFE04-BE-07.md`

- [ ] Write a failing pytest for `POST /pay-lists/{id}/manual-items`.
- [ ] Run `cd backend && pytest -q tests/test_annuity_e2e.py -k pay_list_manual_item`.
- [ ] Implement minimal manual-row creation with nullable `fee_item_id`.
- [ ] Run task-scoped Ruff and pytest.
- [ ] Generate `artifacts/FRFE04-BE-07/**`.
- [ ] Commit only task-allowlist changes.

### Task 9: `FRFE04-FE-01` Shared route/menu/API ownership setup

**Files:**
- Modify: `frontend/src/constants/menu.ts`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/api/govPayments.ts`
- Modify: `frontend/src/api/govPayments.types.ts`
- Spec: `tasks/fr-fe-04/FRFE04-FE-01.md`

- [ ] Add failing type-level or page-import expectations if needed.
- [ ] Wire Fee Management menu entry and route aliases without redesigning unrelated menus.
- [ ] Extend shared API typings only for slices that already have approved backend contracts.
- [ ] Run:
  - `npm run lint -- frontend/src/constants/menu.ts frontend/src/router/index.ts frontend/src/api/govPayments.ts frontend/src/api/govPayments.types.ts`
  - `npm run typecheck`
- [ ] Generate `artifacts/FRFE04-FE-01/**`.
- [ ] Commit only task-allowlist changes.

### Task 10: `FRFE04-FE-02` Pay-list list page

**Files:**
- Modify: `frontend/src/modules/annuity/pages/PayList.vue`
- Modify: `frontend/src/api/govPayments.ts`
- Modify: `frontend/src/api/govPayments.types.ts`
- Spec: `tasks/fr-fe-04/FRFE04-FE-02.md`

- [ ] Make the page fail against missing list/query/export/history-entry behaviors.
- [ ] Implement only list-page closure slice.
- [ ] Run `npm run lint -- frontend/src/modules/annuity/pages/PayList.vue frontend/src/api/govPayments.ts frontend/src/api/govPayments.types.ts`.
- [ ] Run `npm run typecheck`.
- [ ] Generate `artifacts/FRFE04-FE-02/**`.
- [ ] Commit only task-allowlist changes.

### Task 11: `FRFE04-FE-03` Pay-list detail page

**Files:**
- Create: `frontend/src/modules/annuity/pages/PayListDetail.vue`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/api/govPayments.ts`
- Modify: `frontend/src/api/govPayments.types.ts`
- Spec: `tasks/fr-fe-04/FRFE04-FE-03.md`

- [ ] Add page shell and fetch contract for detail endpoint.
- [ ] Implement only detail/read/status/export action visibility.
- [ ] Run task-scoped lint and `npm run typecheck`.
- [ ] Generate `artifacts/FRFE04-FE-03/**`.
- [ ] Commit only task-allowlist changes.

### Task 12: `FRFE04-FE-04` Gov-payment registration page hardening

**Files:**
- Modify: `frontend/src/modules/annuity/pages/GovPaymentCreate.vue`
- Modify: `frontend/src/api/govPayments.ts`
- Modify: `frontend/src/api/govPayments.types.ts`
- Spec: `tasks/fr-fe-04/FRFE04-FE-04.md`

- [ ] Implement only generated-row registration closure slice.
- [ ] Keep all user-visible copy in Simplified Chinese.
- [ ] Run task-scoped lint and `npm run typecheck`.
- [ ] Generate `artifacts/FRFE04-FE-04/**`.
- [ ] Commit only task-allowlist changes.

### Task 13: `FRFE04-FE-05` Manual historical row entry UI

**Files:**
- Create: `frontend/src/modules/annuity/components/ManualGovPaymentDialog.vue`
- Modify: `frontend/src/modules/annuity/pages/PayListDetail.vue`
- Modify: `frontend/src/api/govPayments.ts`
- Modify: `frontend/src/api/govPayments.types.ts`
- Spec: `tasks/fr-fe-04/FRFE04-FE-05.md`

- [ ] Implement only manual-row UI under existing historical pay list.
- [ ] Do not absorb generated-row registration or list-page work.
- [ ] Run task-scoped lint and `npm run typecheck`.
- [ ] Generate `artifacts/FRFE04-FE-05/**`.
- [ ] Commit only task-allowlist changes.

### Task 14: `FRFE04-QA-01` Final close audit

**Files:**
- Modify: `artifacts/FRFE04-QA-01/**`
- Spec: `tasks/fr-fe-04/FRFE04-QA-01.md`

- [ ] Run per-task artifact presence checks.
- [ ] Run `./scripts/task_validate.sh <TASK-ID>` for every executable task.
- [ ] Build item-to-slice ledger for the story.
- [ ] Mark blocked follow-ups separately.
- [ ] Produce final evidence summary.

## Blocked Follow-Ups

These are not executable in this round and must remain separate:

- `FRFE04-BLOCK-01`: `T_PayList` schema fields
- `FRFE04-BLOCK-02`: `T_GovPayment` schema fields
- `FRFE04-BLOCK-03`: structured query fields
- `FRFE04-BLOCK-04`: multi-format official export
- `FRFE04-BLOCK-05`: privileged edit audit log

## Review Notes for Executors

- Backend shared ownership is serialized by wave. Do not run two backend tasks touching `annuity/api.py` or `annuity/service.py` concurrently.
- Frontend shared ownership is serialized by wave. Do not run route/menu/API shared tasks concurrently with page tasks touching the same files.
- SQLite write tests must be serialized.
- `FRFE04-BE-07` manual item endpoint is intentionally separated from `POST /gov-payments` to preserve atomicity.
- Cancellation is deferred unless separately authorized later.
