# Summary

## Commands
- `./scripts/evidence_run.sh DEMO-FE-DOC-01 lint bash -lc "cd frontend && npm run lint"`
- `./scripts/evidence_run.sh DEMO-FE-DOC-01 typecheck bash -lc "cd frontend && npm run typecheck"`
- `./scripts/evidence_run.sh DEMO-FE-DOC-01 test bash -lc "cd frontend && npm run build"`

## Results
- `lint`: passed
- `typecheck`: passed
- `build`: passed

## Notes
- Executed atomic task `DEMO-FE-DOC-01` only.
- Modified only `frontend/src/modules/cases/components/CaseDocumentsTab.vue`.
- Case documents tab now resolves `case_no` via existing cases API and includes both `case_id` and `case_no` in the `/documents/new` route query.
