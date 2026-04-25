# FE Completeness Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the first P0 frontend completeness gaps so finance-chain users can trigger and inspect real backend flows from the UI without direct API calls.

**Architecture:** Use readiness-first remediation. Each task owns one user-facing capability and has its own task file, evidence, allowlist, and verification. Shared frontend API/menu files are serialized.

**Tech Stack:** Vue 3, TypeScript, Vue Router, Element Plus, Axios API wrappers, Vite build/typecheck.

---

## Task 1: Real APPLY_FEE Generation Path

**Files:**
- Create: `tasks/frontend/FE-FEE-APPLY-FEE-GENERATE-01.md`
- Modify: `frontend/src/api/fees.ts`
- Modify: `frontend/src/api/fees.types.ts`
- Modify: `frontend/src/modules/fees/pages/FeeDraftCreate.vue`
- Modify: `frontend/src/modules/fees/pages/FeeDraftDetail.vue`
- Modify: `frontend/src/modules/cases/components/CaseFeesTab.vue`
- Evidence: `artifacts/FE-FEE-APPLY-FEE-GENERATE-01/**`

- [ ] Write task file and dirty baseline evidence.
- [ ] Add a typed API wrapper for `POST /fees/drafts/apply-fee/generate` if missing.
- [ ] Add a user-facing APPLY_FEE generation branch that accepts case id and optional parameters already supported by backend.
- [ ] Route CaseFeesTab to the real APPLY_FEE generation path instead of generic zero draft creation.
- [ ] Keep generic draft creation available for non-APPLY cases.
- [ ] Run frontend typecheck/build or focused checks and task gate.

## Task 2: PayList From GOV Fee Items

**Files:**
- Create: `tasks/frontend/FE-PAYLIST-FROM-FEE-ITEMS-01.md`
- Modify: `frontend/src/api/govPayments.ts`
- Modify: `frontend/src/api/govPayments.types.ts`
- Modify: `frontend/src/modules/annuity/pages/PayList.vue`
- Modify: `frontend/src/modules/annuity/pages/PayListCreate.vue` if present/needed
- Evidence: `artifacts/FE-PAYLIST-FROM-FEE-ITEMS-01/**`

- [ ] Add task file and baseline evidence.
- [ ] Use the existing pay-list-from-fee-items API wrapper or complete its types.
- [ ] Add a UI action for creating a pay list from selected GOV items.
- [ ] Preserve historical/manual pay-list behavior.
- [ ] Run verification and task gate.

## Task 3: PayList Detail Entry

**Files:**
- Create: `tasks/frontend/FE-PAYLIST-DETAIL-ENTRY-01.md`
- Modify: `frontend/src/modules/annuity/pages/PayList.vue`
- Modify: `frontend/src/modules/annuity/pages/PayListDetail.vue`
- Evidence: `artifacts/FE-PAYLIST-DETAIL-ENTRY-01/**`

- [ ] Add task file and baseline evidence.
- [ ] Add a visible detail action from pay-list rows.
- [ ] Confirm detail page exposes enough row information for follow-up registration.
- [ ] Run verification and task gate.

## Task 4: GovPayment From PayList Item

**Files:**
- Create: `tasks/frontend/FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01.md`
- Modify: `frontend/src/modules/annuity/pages/PayListDetail.vue`
- Modify: `frontend/src/modules/annuity/pages/GovPaymentCreate.vue`
- Evidence: `artifacts/FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01/**`

- [ ] Add task file and baseline evidence.
- [ ] Add item-scoped registration entry from pay-list detail.
- [ ] Pass required pay-list and fee-item context into GovPaymentCreate.
- [ ] Keep direct/manual route compatible.
- [ ] Run verification and task gate.

## Task 5: Bill Direction Visibility

**Files:**
- Create: `tasks/frontend/FE-BILL-DIRECTION-VISIBILITY-01.md`
- Modify: `frontend/src/modules/billing/pages/BillList.vue`
- Modify: `frontend/src/modules/billing/pages/BillDetail.vue`
- Evidence: `artifacts/FE-BILL-DIRECTION-VISIBILITY-01/**`

- [ ] Add task file and baseline evidence.
- [ ] Display AR/AP direction in list and detail with Chinese labels.
- [ ] Do not change bill generation behavior.
- [ ] Run verification and task gate.

## Task 6: Payment Create Entry

**Files:**
- Create: `tasks/frontend/FE-PAYMENT-CREATE-ENTRY-01.md`
- Modify: `frontend/src/modules/billing/pages/PaymentList.vue`
- Modify: `frontend/src/modules/billing/pages/PaymentCreate.vue`
- Evidence: `artifacts/FE-PAYMENT-CREATE-ENTRY-01/**`

- [ ] Add task file and baseline evidence.
- [ ] Add visible “新增回款” action.
- [ ] Improve Chinese labels and helper text for pay number/reference semantics.
- [ ] Do not change offset business behavior.
- [ ] Run verification and task gate.

## Task 7: Commission Settleability Visibility

**Files:**
- Create: `tasks/frontend/FE-COMMISSION-SETTLEABILITY-VISIBILITY-01.md`
- Modify: `frontend/src/api/commission.ts` if mapping is incomplete
- Modify: `frontend/src/api/commission.types.ts` if types are incomplete
- Modify: `frontend/src/modules/commission/pages/CommissionList.vue`
- Evidence: `artifacts/FE-COMMISSION-SETTLEABILITY-VISIBILITY-01/**`

- [ ] Add task file and baseline evidence.
- [ ] Show wait-pay, force-settle, and settlement eligibility fields.
- [ ] Add only backend-supported filters.
- [ ] If case-no/bill-no search is unsupported, record backend follow-up instead of faking.
- [ ] Run verification and task gate.

## Task 8: Menu Permission Alignment

**Files:**
- Create: `tasks/frontend/FE-MENU-PERMISSION-ALIGNMENT-01.md`
- Modify: `frontend/src/constants/menu.ts`
- Modify: `frontend/src/constants/perms.ts` if constants are missing
- Evidence: `artifacts/FE-MENU-PERMISSION-ALIGNMENT-01/**`

- [ ] Add task file and baseline evidence.
- [ ] Align PayList menu with `PayList.Read`.
- [ ] Align Commission menus with `Commission.*`, `CommissionRule.*`, and `CommissionSettlement.*` permissions.
- [ ] Do not change backend permission enforcement.
- [ ] Run verification and task gate.

## Task 9: Close Audit

**Files:**
- Create: `tasks/batches/BATCH-FE-COMPLETENESS-REMEDIATION-01-CLOSE-AUDIT.md`
- Create: `docs/frontend/FE_COMPLETENESS_REMEDIATION_CLOSE_AUDIT.md`
- Evidence: `artifacts/BATCH-FE-COMPLETENESS-REMEDIATION-01-CLOSE-AUDIT/**`

- [ ] Map every P0 audit finding to fixed/deferred/blocked.
- [ ] Run final frontend typecheck/build.
- [ ] Record residual blockers and next task IDs.
