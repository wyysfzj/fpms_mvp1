# FPMS SPEC 2.0 Implementation Review Report (Refresh)

**Refresh Date**: 2026-04-03  
**Scope**: Full `Priority-Ranked MISSING Features` re-audit against current workspace state  
**Baseline Type**: `workspace-state`  
**Authority Sources**:
- `docs/FPMS_SPEC2_2nd_Review.md`
- `docs/FPMS SPEC 2.0.md`

This refresh is based on the **current workspace state**, not only committed history. Conclusions below reflect:
- committed implementation added after the old review baseline
- current uncommitted local source changes
- current local spec / plan / task artifacts that materially affect closure interpretation

## 1. Executive Summary

### 1.1 Audit Outcome Snapshot

| Status | Count | Notes |
|---|---:|---|
| Closed | 16 | Fully closed in current workspace-state |
| Partially Closed | 3 | Representative slices exist, but residual gap remains |
| Still Missing | 0 | No item currently lacks sufficient implementation evidence for its core slice |
| Blocked by Prerequisite | 0 | No item currently requires a fresh prerequisite before any further interpretation |
| Needs Reclassification | 1 | Old review framing no longer matches the current implementation reality |

### 1.2 Headline Findings

- The old review is no longer reliable as a current-state source of truth.
- The most outdated old-review regions are:
  - `Fees / Billing operational closure`
  - `Settings query enhancements`
  - `Documents dispatch / envelope / search`
- Several items previously marked `MISSING` are now fully closed in current workspace-state.
- Several other items are not truly `missing` anymore, but should now be interpreted as:
  - `Partially Closed`
  - `Needs Reclassification`
- `P1 #5 多代理人提成分成` is no longer a true missing gap; the original review framing is now out of date relative to the implemented split carrier, commission semantics, and FE exposure.

### 1.3 Recommended Immediate Actions

1. Update the review baseline using this refresh.
2. Reclassify `P2 #13 所有统计报表` as a program-level residual ledger, not a single missing feature.
3. Prioritize:
   1. `P2 #13 所有统计报表 residual decomposition`
   2. `P1 #8 中间文件 5 步向导 residual implementation ledger`
   3. `P2 #15 授权费管理 residual workflow`
   4. `P2 #19 中间文件专项查询 residual DocType gap`

## 2. Current-state Audit Basis

### 2.1 Documents Reviewed

- `docs/FPMS_SPEC2_2nd_Review.md`
- `docs/FPMS SPEC 2.0.md`

### 2.2 Code Areas Reviewed

#### Backend
- `backend/app/modules/cases/**`
- `backend/app/modules/documents/**`
- `backend/app/modules/tasks/**`
- `backend/app/modules/billing/**`
- `backend/app/modules/annuity/**`
- `backend/app/modules/grant_fees/**`
- `backend/app/modules/commission/**`
- `backend/app/modules/masterdata/**`

#### Frontend
- `frontend/src/modules/cases/**`
- `frontend/src/modules/documents/**`
- `frontend/src/modules/tasks/**`
- `frontend/src/modules/billing/**`
- `frontend/src/modules/annuity/**`
- `frontend/src/modules/grantFees/**`
- `frontend/src/modules/settings/**`
- `frontend/src/router/index.ts`
- `frontend/src/api/**`

#### Tests / Migrations / Specs / Plans
- `backend/tests/**`
- `backend/alembic/versions/**`
- `docs/superpowers/specs/**`
- `docs/superpowers/plans/**`
- `tasks/postenhancement/**`

### 2.3 Current Worktree Conditions That Affect Conclusions

| Area | Workspace Finding | Why It Matters |
|---|---|---|
| `backend/app/modules/commission/models.py` | Current uncommitted diff appears formatting-only | Does not change `P1 #5` conclusion |
| `backend/app/modules/annuity/models.py` + related tests | Current uncommitted diffs appear formatting-only | Does not materially change annuity closure conclusion |
| `backend/tests/test_case_receipt_crud.py` + related migration | Current uncommitted diffs appear formatting-only | Does not materially change case receipt closure conclusion |
| `docs/superpowers/plans/**` and `docs/superpowers/specs/**` | Local planning docs exist for grant fee / reports / dispatch / searches | Affects mitigation planning and closure interpretation |
| `tasks/postenhancement/**` | Local task files exist for multiple previously-missing items | Confirms planned/implemented closure slices and residuals |

### 2.4 Why Workspace-state Overrides Committed-state

- The original review baseline was taken on `2026-03-23` against an earlier clean commit.
- The repository now includes substantial implementation beyond that point.
- Some current conclusions depend on local task/spec evidence and current worktree state.
- Therefore, this refresh uses **current real code state** as the source of truth.

## 3. Audit Method

### 3.1 Evaluation Rules

Each review item was re-evaluated against:
1. Old review claim
2. `FPMS SPEC 2.0` intended semantics
3. Current backend implementation
4. Current frontend implementation
5. Current tests / migrations / supporting artifacts
6. Workspace-only evidence where relevant

### 3.2 Status Definitions

- `Closed`
  - Exact closure slice is implemented with sufficient evidence in current workspace-state.
- `Partially Closed`
  - Some closure slices are implemented, but residual gap remains.
- `Still Missing`
  - No sufficient implementation evidence for the core slice.
- `Blocked by Prerequisite`
  - Cannot be honestly closed without a prerequisite slice.
- `Needs Reclassification`
  - Old review interpretation no longer matches the current implementation shape.

### 3.3 Special Cautions Applied

- Representative slice completion does **not** equal full item closure.
- FE-only or BE-only completion does **not** equal full closure unless the item was explicitly scoped that way.
- Spec-semantic drift invalidates a `Closed` claim.
- Workspace-only support must be called out explicitly.

## 4. Item-by-item Re-review

### 4.1 P0 #1 官费清单与缴费 (FR-FE-04)
- **Original Review Claim**: Missing
- **Spec Reference**:
  - Module 4 `费用管理`
  - 官费清单 / 缴费 / 官方付款链路
- **Current Implementation Evidence**:
  - Backend:
    - [annuity/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/annuity/api.py)
      - `POST /pay-lists/from-fee-items`
      - `GET /pay-lists`
      - `GET /pay-lists/{pay_list_id}`
      - `POST /pay-lists/{pay_list_id}/mark-paid`
      - `POST /gov-payments`
      - `POST /pay-lists/{pay_list_id}/manual-items`
  - Frontend:
    - [PayList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/annuity/pages/PayList.vue)
    - [PayListDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/annuity/pages/PayListDetail.vue)
    - [GovPaymentCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/annuity/pages/GovPaymentCreate.vue)
    - [router/index.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/router/index.ts)
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`
- **Why**: pay-list / gov-payment operational closure exists in both BE and FE.
- **Residual Gap**: no residual inside the old review interpretation.
- **Risk**: `Low`

### 4.2 P0 #2 个案收款登记端点 (FR-FE-07)
- **Original Review Claim**: Model exists, need API + UI
- **Spec Reference**:
  - Module 4 `个案收款登记`
- **Current Implementation Evidence**:
  - Backend:
    - [billing/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/api.py)
      - `POST /case-receipts`
      - `PUT /case-receipts/{receipt_id}`
      - `GET /case-receipts`
    - [billing/schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/schemas.py)
    - [test_case_receipt_crud.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_case_receipt_crud.py)
  - Frontend:
    - [CaseReceiptList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/CaseReceiptList.vue)
    - [CaseReceiptDialog.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/components/CaseReceiptDialog.vue)
    - [router/index.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/router/index.ts)
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`
- **Why**: Create/update/list contract and FE page/dialog exist.
- **Residual Gap**: None for this item.
- **Risk**: `Low`

### 4.3 P0 #3 年费管理 API/UI (FR-FE-06)
- **Original Review Claim**: Model exists, need API + UI
- **Spec Reference**:
  - Module 4 `年费管理（多年度）`
- **Current Implementation Evidence**:
  - Backend:
    - [annuity/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/annuity/api.py)
      - `GET /annuity/tasks`
      - `PUT /annuity/tasks/{task_id}/instruction`
      - `POST /annuity/tasks/generate`
      - `POST /annuity/tasks/generate-drafts`
  - Frontend:
    - [AnnuityTaskList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/annuity/pages/AnnuityTaskList.vue)
    - [router/index.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/router/index.ts)
  - Tests:
    - [test_annuity_generate.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_annuity_generate.py)
    - [test_annuity_e2e.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_annuity_e2e.py)
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`

### 4.4 P0 #4 冲销反转前端
- **Original Review Claim**: Backend exists, no frontend UI
- **Spec Reference**:
  - Module 5 `冲销反转`
- **Current Implementation Evidence**:
  - Backend:
    - [billing/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/api.py)
      - `POST /offsets/{offset_id}/reverse`
  - Frontend:
    - [BillDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/BillDetail.vue)
    - [OffsetList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/OffsetList.vue)
    - [PaymentList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/PaymentList.vue)
    - [billing.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/billing.ts) `reverseOffset`
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`

### 4.5 P1 #5 多代理人提成分成 (FR-COM-03)
- **Original Review Claim**: Missing; single-agent model only
- **Spec Reference**:
  - Module 6 `多代理人提成分成`
  - `SecondAgentID` / allocation / ratio semantics
- **Current Implementation Evidence**:
  - Backend carrier and validation:
    - [cases/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/models.py) `T_CaseAgentSplit`
    - [cases/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/service.py) `validate_case_agent_splits(...)`
    - [cases/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/api.py) `agent_splits` output
  - Backend commission semantics:
    - [commission/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/service.py)
      - `_load_case_agent_splits(...)`
      - `_split_money_by_ratios(...)`
      - `apply_commission_for_bill(...)`
      - `_commission_is_rewritable(...)`
      - `recompute_commission_settleable(...)`
      - `generate_commission_settlement_lines(...)`
    - [commission/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/models.py)
      - `Commission.is_settleable`
      - `CommissionSettleLine`
  - Frontend exposure:
    - [CaseCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseCreate.vue)
    - [CaseEdit.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseEdit.vue)
    - [CaseDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseDetail.vue)
  - Close-audit evidence:
    - `artifacts/COMMSPLIT-BE-01/**`
    - `artifacts/COMMSPLIT-BE-02/**`
    - `artifacts/COMMSPLIT-BE-03/**`
    - `artifacts/COMMSPLIT-FE-EDIT-01/**`
    - `artifacts/COMMSPLIT-FE-VIEW-01/**`
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`
- **Why**: Multi-agent split is now functionally closed via case-level split carrier, split-aware commission generation, row-level settlement semantics, and case-side FE editing/viewing. The old review expected a commission-model redesign, but the implemented closure uses `CaseAgentSplit` as the effective carrier.
- **Residual Gap**: no residual remains inside the old review interpretation of `FR-COM-03`.
- **Risk**: `Medium`

### 4.6 P1 #6 坏账完整流程
- **Original Review Claim**: Partial
- **Spec Reference**:
  - Module 5 `坏账标记与恢复`
- **Current Implementation Evidence**:
  - Backend:
    - [billing/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/models.py)
      - `bad_debt_status`
      - `bad_debt_substatus`
      - `BadDebtVoucher`
      - `BadDebtRecovery`
    - [billing/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/api.py)
      - `POST /bills/{bill_id}/bad-debt`
      - `POST /bills/{bill_id}/bad-debt/recover`
      - bill list bad-debt filters
  - Frontend:
    - [BadDebtPanel.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/components/BadDebtPanel.vue)
    - [BillList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/BillList.vue)
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`

### 4.7 P1 #7 预收款管理报表
- **Original Review Claim**: Partial; no dedicated report UI
- **Spec Reference**:
  - Module 5 `预收款管理`
- **Current Implementation Evidence**:
  - Backend:
    - [billing/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/api.py)
      - `GET /payments` with `prepayment_status`, `has_unapplied_only`
    - [billing/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/service.py)
      - prepayment summary computation
  - Frontend:
    - [PaymentList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/PaymentList.vue)
      - page title `预收款管理报表`
      - summary cards + filters + table
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`

### 4.8 P1 #8 中间文件 5 步向导
- **Original Review Claim**: Missing
- **Spec Reference**:
  - Module 2 / wizard architecture
- **Current Implementation Evidence**:
  - Frontend:
    - [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
  - Supporting plan/spec:
    - [2026-03-29-documents-step12-wizard.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/plans/2026-03-29-documents-step12-wizard.md)
    - [2026-03-29-documents-step12-wizard-prereq-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-03-29-documents-step12-wizard-prereq-design.md)
- **Committed-state Conclusion**: Partially Closed
- **Workspace-state Conclusion**: Partially Closed
- **Status**: `Partially Closed`
- **Why**: Wizard shell and Step 1/2 capability exist, and Step 3/4/5 residual contracts have been frozen, but the full 5-step product behavior required by `FPMS SPEC 2.0.md` is not yet implemented.
- **Residual Gap**:
  - Step 3 product implementation
  - Step 4 product implementation
  - Step 5 product implementation
  - full 5-step user path parity
- **Risk**: `High`

### 4.9 P1 #9 时限模板关键字段补全
- **Original Review Claim**: Missing key reminder / deadline fields
- **Spec Reference**:
  - Module 3 / task template semantics
- **Current Implementation Evidence**:
  - [tasks/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/models.py)
  - [tasks/schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/schemas.py)
  - [task_generation_service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/task_generation_service.py)
  - [TaskTemplateList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/system/pages/TaskTemplateList.vue)
  - [tasks.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/tasks.types.ts)
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`
- **Why**: `deadline_base`, `remind_base`, `remind_1/2/3_offset_days`, `daily_remind`, `default_supervisor_id` all exist in carrier, API, generation, and UI.
- **Residual Gap**: None for this item.
- **Risk**: `Low`

### 4.10 P1 #10 案卷缺失字段补全 (~15 fields)
- **Original Review Claim**: Missing fields such as `draw_pages`, `claim_pages`, `to_country`, etc.
- **Spec Reference**:
  - Module 1 / case fields completeness
- **Current Implementation Evidence**:
  - Backend:
    - [cases/schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/schemas.py)
    - [test_case_missing_fields_schema.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_case_missing_fields_schema.py)
    - [test_case_missing_fields_crud.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_case_missing_fields_crud.py)
  - Frontend:
    - [CaseCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseCreate.vue)
    - [CaseEdit.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseEdit.vue)
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`
- **Why**: Missing field set is now present in carrier/schema and exposed in FE create/edit.
- **Residual Gap**: address selection UX can still improve, but field closure is done.
- **Risk**: `Low`

### 4.11 P2 #11 批件递交
- **Original Review Claim**: Missing backend + frontend
- **Spec Reference**:
  - Module 1 `案件递交批处理`
- **Current Implementation Evidence**:
  - Backend:
    - [cases/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/api.py)
      - `GET /cases/batch-filing/candidates`
      - `POST /cases/batch-filing/submit`
  - Frontend:
    - [CaseBatchFiling.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseBatchFiling.vue)
    - [cases.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/cases.ts)
    - [router/index.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/router/index.ts)
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`
- **Why**: Candidate query + submit action + FE page route exist.
- **Residual Gap**: broader status-engine refinement only.
- **Risk**: `Low`

### 4.12 P2 #12 邮寄/交接单/信封
- **Original Review Claim**: Missing tables, endpoints, UI
- **Spec Reference**:
  - Module 2 `FR-WD-08~10`
- **Current Implementation Evidence**:
  - Backend:
    - [documents/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/models.py)
      - `DocDispatch`
      - `DocDispatchLine`
    - [documents/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
      - batch mailing register
      - dispatch create/detail
      - envelope preview
  - Frontend:
    - [DocumentDispatch.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentDispatch.vue)
    - [DocumentEnvelopePrint.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentEnvelopePrint.vue)
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`
- **Why**: Dispatch carrier, mailing batch register, dispatch create/detail, envelope preview page all exist.
- **Residual Gap**: none for the old review item.
- **Risk**: `Low`

### 4.13 P2 #13 所有统计报表
- **Original Review Claim**: All statistical reports missing
- **Spec Reference**:
  - Module 8 reports overview
- **Current Implementation Evidence**:
  - case-report style summary integrated into:
    - [cases/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/service.py)
    - [CaseList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseList.vue)
  - annuity report summary:
    - [annuity/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/annuity/service.py)
    - [AnnuityTaskList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/annuity/pages/AnnuityTaskList.vue)
  - prepayment / billing reporting slices:
    - [PaymentList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/PaymentList.vue)
    - [billing/schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/schemas.py)
  - commission settlement report:
    - [commission/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/commission/api.py)
    - [CommissionSettlement.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/commission/pages/CommissionSettlement.vue)
- **Committed-state Conclusion**: Needs Reclassification
- **Workspace-state Conclusion**: Needs Reclassification
- **Status**: `Needs Reclassification`
- **Why**: This is no longer an honest single `missing` item. Some report families already exist; the residual gap is a report-program decomposition problem.
- **Residual Gap**:
  - case statistics family residuals
  - fee/income family residuals
  - billing aging/bad-debt family residuals
- **Risk**: `Medium`

### 4.14 P2 #14 申请人/国家主数据
- **Original Review Claim**: Missing backend + frontend
- **Spec Reference**:
  - Module 8 settings masterdata
- **Current Implementation Evidence**:
  - Backend:
    - [applicants/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/masterdata/applicants/api.py)
    - [countries/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/masterdata/countries/api.py)
  - Frontend:
    - [ApplicantList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/settings/pages/ApplicantList.vue)
    - [CountryList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/settings/pages/CountryList.vue)
    - [router/index.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/router/index.ts)
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`
- **Why**: CRUD/list/deactivate endpoints and FE pages exist.
- **Residual Gap**: none for this item.
- **Risk**: `Low`

### 4.15 P2 #15 授权费管理
- **Original Review Claim**: Missing model + full workflow
- **Spec Reference**:
  - Module 4 `授权费管理`
- **Current Implementation Evidence**:
  - Backend:
    - [grant_fees/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/grant_fees/api.py)
      - list/state/advance/generate-draft
    - [grant_fees/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/grant_fees/service.py)
  - Frontend:
    - [GrantFeeTaskList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue)
    - [grantFees.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/grantFees.ts)
  - Tests:
    - `test_grant_fee_prereq_*`
    - `test_grant_fee_worklist_api.py`
    - `test_grant_fee_state_machine_api.py`
    - `test_grant_fee_draft_linkage_api.py`
- **Committed-state Conclusion**: Partially Closed
- **Workspace-state Conclusion**: Partially Closed
- **Status**: `Partially Closed`
- **Why**: carrier, worklist, state machine, draft-generation slice exist, but old review item was broader than the first-round implemented workflow.
- **Residual Gap**:
  - broader lifecycle completeness
  - residual downstream workflow/reporting/detail semantics
- **Risk**: `Medium`

### 4.16 P2 #16 费用综合查询
- **Original Review Claim**: Missing dual-table query + UI
- **Spec Reference**:
  - Module 4 `费用情况查询一览`
- **Current Implementation Evidence**:
  - Backend:
    - [billing/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/api.py) `/fee-unified-query`
  - Frontend:
    - [FeeUnifiedQuery.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/FeeUnifiedQuery.vue)
    - [router/index.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/router/index.ts)
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`
- **Why**: first-round unified fee query contract + page exist.
- **Residual Gap**: summary/export/reporting deferred, but old review item itself is closed under approved interpretation.
- **Risk**: `Low`

### 4.17 P2 #17 专项检索
- **Original Review Claim**: Missing APPLY_FEE_LIMIT / EXAM_REQUEST_LIMIT search
- **Spec Reference**:
  - Module 3 `US-DL-07`
- **Current Implementation Evidence**:
  - Backend:
    - [tasks/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/service.py)
      - `SPECIAL_SEARCH_TASK_CODES`
    - related API in tasks module
  - Frontend:
    - [TaskSpecialSearch.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/tasks/pages/TaskSpecialSearch.vue)
    - [router/index.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/router/index.ts)
  - Tests:
    - [test_task_special_search_api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_task_special_search_api.py)
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`
- **Why**: task-code-scoped special search contract and FE page exist.
- **Residual Gap**: none for this item.
- **Risk**: `Low`

### 4.18 P2 #18 高级案件查询增强
- **Original Review Claim**: Missing `applicant_id`, `patent_no`, `fee status` filters
- **Spec Reference**:
  - Module 8 advanced case search
- **Current Implementation Evidence**:
  - Backend:
    - [cases/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/api.py)
      - `applicant_id`
      - `patent_no`
      - `fee_status`
    - [cases/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/cases/service.py)
  - Frontend:
    - [CaseList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/cases/pages/CaseList.vue)
    - [cases.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/cases.types.ts)
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`
- **Why**: approved first-round filter semantics are implemented in both BE and FE.
- **Residual Gap**: no deeper report/drill-down closure implied.
- **Risk**: `Low`

### 4.19 P2 #19 中间文件专项查询
- **Original Review Claim**: Missing document-specific search endpoint
- **Spec Reference**:
  - Module 8 / spec 9.3.2
- **Current Implementation Evidence**:
  - Backend:
    - [documents/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
      - `doc_name`
      - `template_code`
      - `case_no`
      - `need_reply`
      - `replied`
      - `direction`
    - [documents/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
    - [documents/schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/schemas.py)
  - Frontend:
    - [DocumentList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentList.vue)
  - Supporting contract freeze:
    - [2026-04-01-document-specific-search-design.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/docs/superpowers/specs/2026-04-01-document-specific-search-design.md)
- **Committed-state Conclusion**: Partially Closed
- **Workspace-state Conclusion**: Partially Closed
- **Status**: `Partially Closed`
- **Why**: first-round `template_code / doc_name / case_no / need_reply / replied / date / direction` search is closed, but `DocType` independent carrier/filter remains explicitly deferred.
- **Residual Gap**:
  - full spec 9.3.2 parity
  - independent `DocType` semantics
- **Risk**: `Medium`

### 4.20 P2 #20 账单打印前端按钮
- **Original Review Claim**: Backend renderer exists, need frontend button
- **Spec Reference**:
  - Module 5 bill print entry
- **Current Implementation Evidence**:
  - Backend:
    - [billing/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/billing/api.py)
      - `GET /bills/{bill_id}/print`
  - Frontend:
    - [BillDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/BillDetail.vue)
    - [BillList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/BillList.vue)
    - [billing.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/billing.ts) `printBill`
- **Committed-state Conclusion**: Closed
- **Workspace-state Conclusion**: Closed
- **Status**: `Closed`
- **Why**: missing list-page print entry is now closed while reusing existing backend and detail-page print semantics.
- **Residual Gap**: no preview/export/email/history closure implied.
- **Risk**: `Low`

## 5. Gap Report Refresh

### 5.1 Actually Closed Since Old Review

| Item | Title | Notes |
|---|---|---|
| `#1` | 官费清单与缴费 | closed via annuity/pay-list/gov-payment chain |
| `#2` | 个案收款登记端点 | closed via case receipt API + UI |
| `#3` | 年费管理 API/UI | closed via annuity tasks list/API/UI |
| `#4` | 冲销反转前端 | closed via billing FE actions |
| `#6` | 坏账完整流程 | closed via voucher/recovery + FE panel |
| `#7` | 预收款管理报表 | closed via payment list report slice |
| `#9` | 时限模板关键字段补全 | closed in model/API/UI/generation |
| `#10` | 案卷缺失字段补全 | closed for old missing-field interpretation |
| `#11` | 批件递交 | closed via batch filing query/action/page |
| `#12` | 邮寄/交接单/信封 | closed via dispatch + envelope workflow |
| `#14` | 申请人/国家主数据 | closed |
| `#16` | 费用综合查询 | closed first-round |
| `#17` | 专项检索 | closed first-round |
| `#18` | 高级案件查询增强 | closed first-round |
| `#5` | 多代理人提成分成 | closed via `CaseAgentSplit` + commission semantics + FE exposure |
| `#20` | 账单打印前端按钮 | closed |

### 5.2 Still Missing

| Item | Title | Core Missing Slice | Risk |
|---|---|---|---|
| `None` | — | — | — |

### 5.3 Partially Closed

| Item | Title | Implemented Slice | Residual Gap |
|---|---|---|---|
| `#8` | 中间文件 5 步向导 | wizard shell + Step 1/2 + Step 3/4/5 contract freeze | Step 3/4/5 implementation and full 5-step parity |
| `#15` | 授权费管理 | carrier + worklist + state + draft generation | broader workflow residual |
| `#19` | 中间文件专项查询 | first-round document-specific search | `DocType` residual semantics |

### 5.4 Blocked by Prerequisite

| Item | Title | Blocking Prerequisite | Notes |
|---|---|---|---|
| `None` | — | — | No item currently requires a fresh prerequisite just to preserve current interpretation |

### 5.5 Needs Reclassification

| Item | Title | Old Framing | Recommended New Framing |
|---|---|---|---|
| `#13` | 所有统计报表 | single missing feature | multi-family reporting residual program |

### 5.6 Likely False Positives in Old Review

| Item | Why Old Review Is Now Too Pessimistic |
|---|---|
| `#12` | dispatch / handoff / envelope workflow now exists |
| `#14` | applicant and country masterdata now exist in BE/FE |
| `#16` | first-round fee unified query is implemented |
| `#17` | special task search now exists |
| `#18` | advanced case filters now exist |
| `#5` | functional closure now exists through `CaseAgentSplit` + split-aware commission semantics |
| `#20` | list-page print entry now exists |

### 5.7 Likely False Negatives / Coarse Framing in Old Review

| Item | Why Old Review Framing Is Now Too Coarse |
|---|---|
| `#13` | report family now needs decomposition, not a binary missing judgment |
| `#15` | current implementation is no longer `missing`, but not fully closed |
| `#19` | current query slice exists but does not yet close full spec parity |

## 6. Final Judgment

### 6.1 Most Unreliable Areas in the Old Review

- `Fees / Billing operational flow gaps`
- `Documents dispatch / envelope / query gaps`
- `Settings search enhancements`
- `Reports as a single missing block`

### 6.2 Highest-value Gaps to Prioritize Next

1. `P1 #5 多代理人提成分成`
1. `P2 #13 所有统计报表 residual decomposition`
2. `P1 #8 中间文件 5 步向导 residual implementation ledger`
3. `P2 #15 授权费管理 residual workflow`
4. `P2 #19 中间文件专项查询 residual DocType slice`

### 6.3 Items That Should Not Go Straight to Implementation

- `#13` → reclassification first
- `#19` → residual contract freeze first

### 6.4 Items That Need Review Baseline Update Immediately

- `#12`
- `#14`
- `#16`
- `#17`
- `#18`
- `#5`
- `#20`

## Appendix A. Old Review Position vs Current Workspace Finding

| Item | Old Review Position | Current Workspace Finding | Reason For Divergence |
|---|---|---|---|
| `#12` | Missing | Closed | dispatch/envelope workflow added after baseline |
| `#14` | Missing | Closed | applicant/country BE+FE now exist |
| `#16` | Missing | Closed | fee unified query added |
| `#17` | Missing | Closed | task special search added |
| `#18` | Missing | Closed | advanced case filters added |
| `#5` | Missing | Closed | `CaseAgentSplit` carrier + commission semantics + case-side FE exposure now close the functional item |
| `#8` | Missing | Partially Closed | Step1/2 representative slices exist and residual contracts are frozen, but full 5-step product implementation is still missing |
| `#19` | Missing | Partially Closed | first-round search exists, full spec parity not yet |
| `#20` | Missing | Closed | missing list-page print entry added |

## Appendix B. Notes on Committed-state vs Workspace-state

| Item | Committed-state Conclusion | Workspace-state Conclusion | Why |
|---|---|---|---|
| `#13` | Needs Reclassification | Needs Reclassification | current repo already contains multiple report-family slices |
| `#8` | Partially Closed | Partially Closed | contract-freeze work exists, but strict spec-parity closure still requires Step3/4/5 implementation |
| `#15` | Partially Closed | Partially Closed | first-round workflow present, but not full spec breadth |
| `#19` | Partially Closed | Partially Closed | residual `DocType` semantics still open |
| `#5` | Closed | Closed | committed COMMSPLIT chain now closes carrier + semantics + FE exposure |
