# PE-BE-CS-06 Evidence Summary

## Task
- Task ID: `PE-BE-CS-06`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-06.md`
- Scope (allowlist):
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/billing/service.py`

## Implemented
1. Added consulting helper in `consulting/service.py`:
   - `filter_consulting_search_case_ids(db, case_ids)`
   - returns deterministic, sorted case IDs where `case_type in {CONSULTING, SEARCH}`.
2. Integrated new non-blocking recompute hook in billing chain:
   - added `_run_consulting_commission_recompute_non_blocking(...)` in `billing/service.py`
   - flow: collect service case IDs from bill -> filter consulting/search cases -> call
     `recompute_commission_settleable(..., strict=False)`.
3. Wired hook after commission apply hook for bill generation paths:
   - `generate_bill(...)`
   - `generate_bill_from_drafts(...)`
4. Preserved non-intrusive billing success path:
   - exceptions are caught/logged; billing return contract unchanged.
5. `backend/app/modules/commission/service.py` required no code change for this integration.

## How Candidate Entry Is Ensured
- Billing now performs both side effects in sequence after bill persistence:
  1) `apply_commission_for_bill(strict=False)` writes/updates commission rows.
  2) for consulting/search service cases on the same bill, `recompute_commission_settleable(strict=False)` runs immediately.
- This ensures newly written consulting/search commissions enter settleable-candidate lifecycle without affecting billing success.

## Verification
- `./scripts/evidence_run.sh PE-BE-CS-06 lint bash -lc 'cd backend && ruff check app/modules/consulting/service.py app/modules/commission/service.py app/modules/billing/service.py && ruff format --check app/modules/consulting/service.py app/modules/commission/service.py app/modules/billing/service.py'`
  - `rc=0`
- `./scripts/evidence_run.sh PE-BE-CS-06 test bash -lc 'cd backend && pytest -q'`
  - `rc=0` (`141 passed, 3 warnings`)

## Semantics
- Billing API success semantics unchanged.
- Commission/apply/recompute side effects remain non-blocking in billing path (`strict=False`).
- Side-effect failures are logged and do not fail bill generation.

## Evidence Files
- `artifacts/PE-BE-CS-06/results.jsonl`
- `artifacts/PE-BE-CS-06/summary.md`
- `artifacts/PE-BE-CS-06/git/diff.patch`
