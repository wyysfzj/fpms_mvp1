# B4 Findings

## Bugs Found
_None_

## Deviations from Plan
_None yet_

## Discoveries

### 1. FeeRate original migration (0004_fees) has no audit columns
The original `0004_fees` migration created `t_fee_rate` WITHOUT `created_at`, `updated_at`, `created_by`, `updated_by` columns. However, the FeeRate model inherits `AuditMixin`. A later migration (`e109a0b1c2d3_enh10_add_audit_columns.py`) presumably added these columns. This means the B4 migration doesn't need to worry about audit columns — they should already exist.

### 2. CalcMode enum doesn't exist yet
`enums.py` only has `FeeType` and `FeeDraftStatus`. We need to add `CalcMode` (FIXED, PER_CLAIM, PER_PAGE, TIER) as part of B4.

### 3. Case model has all fields needed for future calc
`T_Case` already has `case_type`, `patent_category`, `claim_count`, `spec_pages`, and `fee_reduction` — all fields that would be needed for PER_CLAIM/PER_PAGE/TIER calculations in a future batch. The `calculate_fee_amount(rate, case)` signature is future-proof.

### 4. create_fee_rate uses explicit field assignment (not model_dump)
The `create_fee_rate` service function explicitly sets each field on the `FeeRate` constructor rather than using `data.model_dump()`. This means we must add the 9 new fields explicitly to the constructor call. The `update_fee_rate` function uses `model_dump(exclude_unset=True)` + `setattr` loop, which will automatically handle new fields without code changes.

### 5. Migration chain is linear
Latest revision: `b2_doc_reply_01`. Our new migration `b4_fee_rate_dims_01` will depend on it. The naming jumps from b2 to b4 (no b3 migration file — B3 was purely code changes, no schema change).

### 6. list_fee_rates existing filters use simple equality
All filters use `== value` comparison. New dimension filters should follow the same pattern for consistency.
