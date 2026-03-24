# PE-FE-FE-03

Status: PASS

Scope:
- `frontend/src/modules/fees/components/FeeRateForm.vue`

Changes:
- added Batch 3 helper copy for `PER_CLAIM` calc parameters
- made the calc-params placeholder explicit for `per_claim_amount`, `discount_pct`, and `reduction_pct`
- clarified when `reduction_pct` is ignored unless `allow_reduction` is enabled

Validation:
- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`

Notes:
- no route changes
- no billing UI spillover
- no document generation scope added
- this is one frontend closure slice only; broader fees overview work remains in later Batch 3 waves
