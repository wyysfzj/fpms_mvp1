# Summary

## Commands
- `cd frontend && npm run lint -- src/api/fees.ts src/api/fees.types.ts src/modules/fees/pages/FeeDraftList.vue`
- `cd frontend && npm run typecheck`

## Results
- Wired the new fee balance summary fields into `fees.ts` and `fees.types.ts`.
- Added a Simplified-Chinese billed / received / unpaid summary block to `FeeDraftList.vue`.
- Preserved the existing grouped summary sections and page flow.

## Notes
- This task does not create a new report page.
- Chart, export, and trend views remain deferred.
