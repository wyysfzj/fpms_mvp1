# PD-FEE-SCENARIO-REDUCTION-SEMANTICS-FIX-20260705-01

Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice
- Update the official-fee application fee calculation and P1 live demo fixtures to use the user-confirmed fee-reduction semantics:
  - `fee_reduction=0.85` means 85% reduction and 15% payable.
  - `fee_reduction=0.70` means 70% reduction and 30% payable.
  - invention application fee is 900 RMB, not 1000 RMB.
- Keep generated application-fee items official-fee-only (`fee_type=GOV`) and preserve existing open-draft idempotency.

## Explicit Non-Closure
- No database schema migration.
- No new fee category/subtype columns.
- No PCT, Hague, IC layout, restoration, extension, invalidation, compensation-period, open-license, official payment Excel, CPC/OA direct integration, RPA, automatic payment, or new trigger-rule table implementation.
- No unrelated billing, receipt, commission, grant-fee, annuity, or frontend redesign changes beyond updating affected assertions/fixtures for the corrected application-fee semantics.

## Remaining Follow-Up Task IDs
- `PD-FEE-SCENARIO-CATEGORY-SUBTYPE-MODEL-20260705-01` if category/subtype fields are implemented later.
- `PD-FEE-SCENARIO-DEADLINE-RULES-20260705-01` if structured deadline fields are implemented later.
- `PD-FEE-SCENARIO-PCT-HAGUE-CATALOG-20260705-01` if PCT/Hague catalog rules are implemented later.

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-REDUCTION-SEMANTICS-FIX-20260705-01.md
- backend/app/modules/fees/service.py
- backend/tests/test_apply_fee_draft_rule.py
- backend/tests/test_apply_bill_readiness.py
- backend/tests/test_apply_bill_unhappy.py
- backend/tests/test_apply_fee_item_validation.py
- backend/tests/test_apply_gov_paylist_readiness.py
- backend/tests/test_payment_offset_case_receipt_readiness.py
- backend/tests/test_commission_rule_seed_readiness.py
- backend/tests/test_commission_waitpay_threshold.py
- backend/tests/test_official_fee_preview_api.py
- FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py
- FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts
- artifacts/PD-FEE-SCENARIO-REDUCTION-SEMANTICS-FIX-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-REDUCTION-SEMANTICS-FIX-20260705-01.md`
- `cd backend && PYTHONPATH=. pytest tests/test_apply_fee_draft_rule.py tests/test_apply_bill_readiness.py tests/test_apply_bill_unhappy.py tests/test_apply_fee_item_validation.py tests/test_apply_gov_paylist_readiness.py tests/test_payment_offset_case_receipt_readiness.py tests/test_commission_rule_seed_readiness.py tests/test_commission_waitpay_threshold.py tests/test_official_fee_preview_api.py -q`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx tsc --noEmit`
- `ruff check --fix backend/app/modules/fees/service.py backend/tests/test_apply_fee_draft_rule.py backend/tests/test_apply_bill_readiness.py backend/tests/test_apply_bill_unhappy.py backend/tests/test_apply_fee_item_validation.py backend/tests/test_apply_gov_paylist_readiness.py backend/tests/test_payment_offset_case_receipt_readiness.py backend/tests/test_commission_rule_seed_readiness.py backend/tests/test_commission_waitpay_threshold.py backend/tests/test_official_fee_preview_api.py`
- `ruff format backend/app/modules/fees/service.py backend/tests/test_apply_fee_draft_rule.py backend/tests/test_apply_bill_readiness.py backend/tests/test_apply_bill_unhappy.py backend/tests/test_apply_fee_item_validation.py backend/tests/test_apply_gov_paylist_readiness.py backend/tests/test_payment_offset_case_receipt_readiness.py backend/tests/test_commission_rule_seed_readiness.py backend/tests/test_commission_waitpay_threshold.py backend/tests/test_official_fee_preview_api.py`
- `ruff check backend/app/modules/fees/service.py backend/tests/test_apply_fee_draft_rule.py backend/tests/test_apply_bill_readiness.py backend/tests/test_apply_bill_unhappy.py backend/tests/test_apply_fee_item_validation.py backend/tests/test_apply_gov_paylist_readiness.py backend/tests/test_payment_offset_case_receipt_readiness.py backend/tests/test_commission_rule_seed_readiness.py backend/tests/test_commission_waitpay_threshold.py backend/tests/test_official_fee_preview_api.py`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-REDUCTION-SEMANTICS-FIX-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-REDUCTION-SEMANTICS-FIX-20260705-01/**

## Done Definition
- Targeted backend tests prove `fee_reduction=0.85` produces 15% payable amounts for reducible official application-fee items.
- Targeted backend tests prove the invention application fee source amount is 900 RMB.
- P1 live demo seed and E2E assertions use the corrected 900 RMB application fee and 15% payable amount.
- Task gate and evidence artifacts pass.
