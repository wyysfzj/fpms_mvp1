# PE-BE-CS-05 Evidence Summary

## Task
- Task ID: `PE-BE-CS-05`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-05.md`
- Scope (allowlist):
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`

## Implemented
1. Added endpoint `POST /consulting/fee-drafts` in consulting API.
2. Added permission injection exactly:
   - `_perm: None = Depends(require_perm("ConsultingFeeDraft.Create"))`
3. Added request models supporting mode inputs:
   - `mode` (`FIXED` / `HOURLY` / `HYBRID`)
   - `fixed_fee`
   - `hourly_lines` (`fee_code`, `fee_name`, `hours`, `hourly_rate`, optional remark/trace_key)
   - `misc_lines` (`fee_code`, `fee_name`, `amount`, optional remark/trace_key)
4. Delegated generation logic to CS-04 service interface:
   - `generate_consulting_fee_draft(...)`
5. Response status and shape:
   - HTTP `201`
   - returns: `draft_id`, `draft_type`, `mode`, `currency`, `totals`, `items`, `created_line_count`
6. Existing consulting case endpoint behavior remains unchanged.

## Verification
- `./scripts/evidence_run.sh PE-BE-CS-05 lint bash -lc 'cd backend && ruff check app/modules/consulting/api.py app/modules/consulting/service.py && ruff format --check app/modules/consulting/api.py app/modules/consulting/service.py'`
  - `rc=0`
- `./scripts/evidence_run.sh PE-BE-CS-05 test bash -lc 'cd backend && pytest -q'`
  - `rc=0` (`141 passed, 3 warnings`)

## Expected Semantics
- `201`: fee draft generation success
- `400`: invalid mode/inputs from strategy validation
- `404`: target case not found
- `409`: open-draft conflict from strategy guard
- `422`: request schema/type validation failures

## Evidence Files
- `artifacts/PE-BE-CS-05/results.jsonl`
- `artifacts/PE-BE-CS-05/summary.md`
- `artifacts/PE-BE-CS-05/git/diff.patch`
