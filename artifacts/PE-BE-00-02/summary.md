# PE-BE-00-02 Evidence Summary

## Task
- ID: PE-BE-00-02
- Runbook: `tasks/postenhancement/backend/PE-BE-00-02.md`

## Scope Compliance
- Code/doc changes restricted to allowlist:
  - `backend/app/modules/rbac/service.py`
  - `docs/permissions_matrix.md`
- No runtime changes outside allowlist.

## Changes Implemented
- Added new-domain permission constants to `ROLE_PERMISSIONS["Admin"]` with full coverage for planned domains:
  - `AnnuityTask.Read`
  - `AnnuityTask.Action`
  - `PayList.Create`
  - `GovPayment.Create`
  - `Dunning.Create`
  - `Dunning.Read`
  - `BadDebt.Action`
  - `CommissionRule.Create`
  - `CommissionRule.Read`
  - `CommissionRule.Edit`
  - `Commission.Read`
  - `CommissionSettlement.Create`
  - `CommissionSettlement.Action`
  - `CommissionReport.Read`
  - `ConsultingCase.Create`
  - `ConsultingFeeDraft.Create`
  - `Expense.Create`
  - `Expense.Read`
- Hardened seed idempotency/dedup safety:
  - iterate with `dict.fromkeys(perm_codes)`
  - update `existing_codes` immediately after adding a perm
- Updated `docs/permissions_matrix.md` to match runtime permission contracts for planned endpoints in:
  - Annuity
  - Collections (Dunning/Bad Debt)
  - Commission
  - Consulting/Search/Expense

## Verification
- Required:
  - `cd backend && pytest -q tests/test_system_params.py` -> PASS (`6 passed, 3 warnings`)
- Optional:
  - `cd backend && python3 scripts/scan_perms.py` -> PASS (script present and executed)

## Notes
- Permission naming kept in `Title.Action` style.
- Seed remains idempotent and now defensively avoids duplicate in-run role-perm inserts.
