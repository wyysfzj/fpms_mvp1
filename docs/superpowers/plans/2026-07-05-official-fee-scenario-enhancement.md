# Official Fee Scenario Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved post-demo official-fee enhancement so FPMS can generate official-fee-only drafts from case lifecycle, file, and task events, with verifiable tests and evidence.

**Architecture:** Reuse the existing `FeeRate`, `FeeDraft`, `FeeItem`, `PayList`, `GovPayment`, `GrantFeeTask`, and `AnnuityTask` tables. `FeeRate` is the official-fee parameter table for customer DOCX, Tianyue URL, and later official-policy source entries. Generated fee items in this enhancement are `GOV` only; there is no management-fee or service-fee scope. Add small service-layer rules that convert case context into official-fee candidate items. Avoid broad UI or schema work until backend official-fee behavior is stable.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite-compatible models/migrations, pytest, Vue for later UI slices.

---

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Batch Manifest

| Wave | Task ID | Task File | Closure | Owner | Dependency |
| --- | --- | --- | --- | --- | --- |
| 1 | `PD-FEE-SCENARIO-APPLY-GOV-ONLY-20260705-01` | `tasks/postdemo/PD-FEE-SCENARIO-APPLY-GOV-ONLY-20260705-01.md` | Application fee draft generation uses official-fee-only scenario rules and no longer creates service-fee items. | backend | None |
| 2 | `PD-FEE-SCENARIO-RATE-METADATA-20260705-01` | `tasks/postdemo/PD-FEE-SCENARIO-RATE-METADATA-20260705-01.md` | FeeRate API can carry source/version/status metadata for customer DOCX, Tianyue URL, and official policy source. | backend | Wave 1 |
| 3 | `PD-FEE-SCENARIO-RATE-CATALOG-SEED-20260705-01` | `tasks/postdemo/PD-FEE-SCENARIO-RATE-CATALOG-SEED-20260705-01.md` | Load the customer DOCX / Tianyue URL official-fee entries into `FeeRate` as auditable parameters, with complex items allowed to remain disabled or pending confirmation. | backend | Wave 2 |
| 4 | `PD-FEE-SCENARIO-ANNUITY-GOV-RATE-20260705-01` | `tasks/postdemo/PD-FEE-SCENARIO-ANNUITY-GOV-RATE-20260705-01.md` | Annuity task fee prefill selects GOV annual rates by patent category/year tier and does not depend on service rates. | backend | Waves 1-3 |
| 5 | `PD-FEE-SCENARIO-GRANT-GOV-RATE-20260705-01` | `tasks/postdemo/PD-FEE-SCENARIO-GRANT-GOV-RATE-20260705-01.md` | Grant fee task/draft linkage derives official fee amounts from GOV rate rules. | backend | Waves 1-3 |
| 6 | `PD-FEE-SCENARIO-OFFICIAL-FEE-PREVIEW-20260705-01` | `tasks/postdemo/PD-FEE-SCENARIO-OFFICIAL-FEE-PREVIEW-20260705-01.md` | File/official-document events can preview official fee candidates with source event and idempotency key. | backend | Waves 1-5 |
| 7 | `PD-FEE-SCENARIO-FEE-NODE-UI-20260705-01` | `tasks/postdemo/PD-FEE-SCENARIO-FEE-NODE-UI-20260705-01.md` | Case/document UI shows simplified Chinese official-fee node status and calculation basis. | frontend | Waves 1-6 |
| 8 | `PD-FEE-SCENARIO-E2E-VERIFY-20260705-01` | `tasks/postdemo/PD-FEE-SCENARIO-E2E-VERIFY-20260705-01.md` | End-to-end verification covers new application fee, grant fee, annuity, pay list, and UI fee node flow. | tester | Waves 1-7 |

## Task 1: Application Official Fee Scenario

**Files:**
- Modify: `backend/app/modules/fees/service.py`
- Modify: `backend/tests/test_apply_fee_draft_rule.py`
- Modify: `backend/tests/test_apply_gov_paylist_readiness.py`
- Modify: `backend/tests/test_apply_fee_item_validation.py`

- [ ] **Step 1: Write failing tests**
  - Update apply-fee tests so seeded rates are official-fee-only.
  - Assert generated draft has `total_service=0`, `total_misc=0`, and all items are `GOV`.
  - Assert domestic invention with `has_exam_request=True` can generate application fee, excess claim fee, publication fee, and substantive exam fee from `FeeRate`.

- [ ] **Step 2: Verify RED**
  - Run: `pytest backend/tests/test_apply_fee_draft_rule.py -q`
  - Expected: FAIL because current implementation still requires and creates `APPLY_SERVICE`.

- [ ] **Step 3: Implement minimal service change**
  - Replace service-fee requirement with official-fee scenario item selection.
  - Keep idempotency of one open `APPLY_FEE` draft per case/currency.
  - Keep existing error envelope and 409 missing-rate semantics.

- [ ] **Step 4: Verify GREEN**
  - Run targeted apply-fee and pay-list readiness tests.
  - Run task gate.

## Remaining Tasks

Tasks 2-8 must each get their own atomic task file before implementation. Do not absorb them into Task 1.

The rate catalog seed task must distinguish two states:

- `FeeRate` parameter coverage: official-fee entries from customer DOCX / Tianyue URL are represented as auditable master data with source metadata.
- Executable trigger coverage: only confirmed domestic-mainline rows are enabled for automatic preview or draft generation in P1.5; complex PCT, international-design, compensation-period, and policy-sensitive rows can remain disabled or pending confirmation.
