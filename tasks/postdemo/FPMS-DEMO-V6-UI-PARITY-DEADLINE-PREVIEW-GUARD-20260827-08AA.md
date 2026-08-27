# FPMS-DEMO-V6-UI-PARITY-DEADLINE-PREVIEW-GUARD-20260827-08AA

Risk: HIGH
Closure-Tags: lifecycle, ui
Runbook: P0-single-lane-story
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-DEADLINE-PREVIEW-GUARD-20260827-08AA.md

## Design references

- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `backend/app/modules/documents/service.py::_merge_document_create_extra_data`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`

## Exact Closure Slice

Exact atomic anchor: `frontend/src/modules/documents/pages/DocumentCreate.vue::fetchImpactPreview`.

Prevent document impact-preview requests while the official-deadline tuple is partially
populated. The preview remains enabled when all three deadline fields are empty or when all
three are present. This closes the normal manual-input 400 responses observed in Stage 06.

## Scope decision — FIXED

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: frontend-only behavior guard; backend contract is unchanged
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`
- Implement exactly one incomplete-tuple guard in `fetchImpactPreview`.
- Add one focused executable contract regression for empty, partial, and complete tuples.
- Resume the existing Stage 06/07 dynamic tracer only after this task is independently accepted.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-DEADLINE-PREVIEW-GUARD-20260827-08AA.md`
- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `frontend/tests/demo-v6-lifecycle-ui-contract.mjs`

## Explicit Non-Closure

- No backend, API, schema, deadline semantics, template, or fee behavior changes.
- No retry, debounce, sleep, error filtering, or console/network suppression.
- No change to `DocumentWizard.vue`, `DocumentEdit.vue`, or other forms.
- No Stage 07 or later implementation.
- No adjacent cleanup, abstraction, renaming, or formatting.

## Verification Commands

1. Focused RED then GREEN: `node frontend/tests/demo-v6-lifecycle-ui-contract.mjs`.
2. Typecheck: `npm run typecheck` from `frontend/`.
3. Scoped lint: ESLint only the two allowlisted frontend files.
4. Scope and `git diff --check` for this exact task.
5. Independent HIGH findings-only review with `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`.
6. Atomic evidence validation after independent review.

## Evidence Path

`artifacts/FPMS-DEMO-V6-UI-PARITY-DEADLINE-PREVIEW-GUARD-20260827-08AA/`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08` resumes at Stage 06 clean-network checkpoint,
  then Stage 07.

## Prompt

Implement only the fixed closure above. Do not add optional behavior or absorb any follow-up.
