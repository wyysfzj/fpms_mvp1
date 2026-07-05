# PD-FEE-SCENARIO-APPLY-GOV-ONLY-20260705-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Change `/api/v1/fees/drafts/apply-fee/generate` so domestic application fee draft generation is official-fee-only:

- It must not require or create `APPLY_SERVICE` or any non-official fee item.
- Generated `FeeItem` rows from this endpoint must have `fee_type=GOV`.
- Generated `FeeDraft.total_service` and `FeeDraft.total_misc` must be `0`.
- The endpoint must generate official application fee candidates from enabled `FeeRate` rows:
  - base application fee by patent category using `CN_INV_APPLICATION_FEE`, `CN_UM_APPLICATION_FEE`, or `CN_DES_APPLICATION_FEE`;
  - excess claim fee using `CN_EXCESS_CLAIM_FEE` when `claim_count > 10`;
  - publication printing fee using `CN_PUBLICATION_PRINT_FEE` for invention cases;
  - substantive exam fee using `CN_SUBSTANTIVE_EXAM_FEE` when an invention case has `has_exam_request=True`.
- Missing required official fee rates for the case context must still return `APPLY_FEE_RATE_MISSING` with the missing fee codes.
- Existing open-draft idempotency must remain unchanged.

## Explicit Non-Closure

- No frontend changes.
- No database migration or new table.
- No FeeRate source/version/status metadata implementation.
- No annuity, grant-fee, OA, PCT, reexamination, restoration, extension, invalidation, or official-payment Excel implementation.
- No service-fee, miscellaneous-fee, management-fee, billing, or receipt workflow changes.

## Remaining Follow-Up Task IDs

- `PD-FEE-SCENARIO-RATE-METADATA-20260705-01`
- `PD-FEE-SCENARIO-ANNUITY-GOV-RATE-20260705-01`
- `PD-FEE-SCENARIO-GRANT-GOV-RATE-20260705-01`
- `PD-FEE-SCENARIO-OFFICIAL-FEE-PREVIEW-20260705-01`
- `PD-FEE-SCENARIO-FEE-NODE-UI-20260705-01`
- `PD-FEE-SCENARIO-E2E-VERIFY-20260705-01`

## Allowed Files

- `tasks/postdemo/PD-FEE-SCENARIO-APPLY-GOV-ONLY-20260705-01.md`
- `docs/superpowers/plans/2026-07-05-official-fee-scenario-enhancement.md`
- `backend/app/modules/fees/service.py`
- `backend/tests/test_apply_fee_draft_rule.py`
- `backend/tests/test_apply_gov_paylist_readiness.py`
- `backend/tests/test_apply_fee_item_validation.py`
- `backend/tests/test_apply_bill_readiness.py`
- `backend/tests/test_apply_bill_unhappy.py`
- `backend/tests/test_payment_offset_case_receipt_readiness.py`
- `backend/tests/test_commission_rule_seed_readiness.py`
- `backend/tests/test_commission_waitpay_threshold.py`
- `artifacts/PD-FEE-SCENARIO-APPLY-GOV-ONLY-20260705-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-APPLY-GOV-ONLY-20260705-01.md`
- `cd backend && PYTHONPATH=. pytest tests/test_apply_fee_draft_rule.py -q`
- `cd backend && PYTHONPATH=. pytest tests/test_apply_fee_draft_rule.py tests/test_apply_gov_paylist_readiness.py tests/test_apply_fee_item_validation.py tests/test_apply_bill_readiness.py tests/test_apply_bill_unhappy.py tests/test_payment_offset_case_receipt_readiness.py tests/test_commission_rule_seed_readiness.py tests/test_commission_waitpay_threshold.py -q`
- `ruff check --fix backend/app/modules/fees/service.py backend/tests/test_apply_fee_draft_rule.py backend/tests/test_apply_gov_paylist_readiness.py backend/tests/test_apply_fee_item_validation.py backend/tests/test_apply_bill_readiness.py backend/tests/test_apply_bill_unhappy.py backend/tests/test_payment_offset_case_receipt_readiness.py backend/tests/test_commission_rule_seed_readiness.py backend/tests/test_commission_waitpay_threshold.py`
- `ruff format backend/app/modules/fees/service.py backend/tests/test_apply_fee_draft_rule.py backend/tests/test_apply_gov_paylist_readiness.py backend/tests/test_apply_fee_item_validation.py backend/tests/test_apply_bill_readiness.py backend/tests/test_apply_bill_unhappy.py backend/tests/test_payment_offset_case_receipt_readiness.py backend/tests/test_commission_rule_seed_readiness.py backend/tests/test_commission_waitpay_threshold.py`
- `ruff check backend/app/modules/fees/service.py backend/tests/test_apply_fee_draft_rule.py backend/tests/test_apply_gov_paylist_readiness.py backend/tests/test_apply_fee_item_validation.py backend/tests/test_apply_bill_readiness.py backend/tests/test_apply_bill_unhappy.py backend/tests/test_payment_offset_case_receipt_readiness.py backend/tests/test_commission_rule_seed_readiness.py backend/tests/test_commission_waitpay_threshold.py`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-APPLY-GOV-ONLY-20260705-01`

## Evidence Path

- `artifacts/PD-FEE-SCENARIO-APPLY-GOV-ONLY-20260705-01/`

## Done Definition

- Targeted tests prove application fee generation is official-fee-only and still supports PayList/GovPayment readiness for generated GOV items.
- Task gate passes.
