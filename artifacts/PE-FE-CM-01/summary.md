# PE-FE-CM-01 Evidence Summary

- Task file: `tasks/postenhancement/frontend/PE-FE-CM-01.md`
- Role: `worker`
- Scope mode: narrow takeover / review-only
- Product code edited in this takeover: none
- Evidence patch: `artifacts/PE-FE-CM-01/git/diff.patch`

## Allowlist review

- Allowlist files with current diff:
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
- `frontend/src/api/clients.ts` is allowlisted but currently has no diff.
- Current frontend worktree also contains many out-of-allowlist changes, including:
  - `frontend/src/constants/displayText.ts`
  - `frontend/src/constants/labels.zh.ts`
  - `frontend/src/constants/workflow.ts`
  - `frontend/src/modules/clients/pages/ClientDetail.vue`
  - `frontend/src/modules/clients/pages/ClientForm.vue`
  - `frontend/src/modules/clients/pages/ClientList.vue`
  - multiple Batch 2+/other-domain pages under `billing`, `fees`, `commission`, `consulting`, `documents`, `system`, `annuity`
- Conclusion: the allowlist subset is reviewable, but the current overall frontend batch is not task-scope clean for `PE-FE-CM-01`.

## Batch 1 coverage observed in allowlist diff

- `US-CM-01` / `FR-CM-02`:
  - create/edit pages now add pre-submit validation summary and grouped field errors.
  - status -> `app_no` / `filing_date` linkage is enforced on edit.
  - priority completeness is enforced on create/edit.
- `US-CM-02` / `FR-CM-05`:
  - create/edit pages now show conditional sections by `case_type`.
  - priority records support `0..n` add/remove and detail display.
  - publication/specification/control sections are hidden for consulting/search case types.
- `US-CM-03` / `FR-CM-03`:
  - create page adds customer quick-create dialog and auto-fill back into case form.
  - this depends on pre-existing `createClient` support from `frontend/src/api/clients.ts`; no new diff exists in that file.
- `FR-CM-04`:
  - detail page now shows case type, patent category, flow direction, application number, priority list, and status automation hint for readonly workflow states.
  - case API mapping/types now include `case_type`, `patent_category`, `flow_dir`, and `priorities`.

## Verification

- Main thread previously reported `npm run lint` passed.
- Main thread previously reported `npm run typecheck` passed.
- This takeover re-ran only review/scope-audit commands and generated scoped evidence.
- Manual flow verification was not re-executed in this takeover.

## Risks / gaps

- Scope compliance risk:
  - current frontend worktree includes many files outside this task allowlist, so this task cannot be claimed cleanly complete as a standalone atomic batch.
- Acceptance gap:
  - manual `Case Create / Edit / Detail` verification is still only referenced, not re-executed here.
- Functional gap:
  - `FR-CM-03` spec mentions customer/applicant/foreign-agent quick create; the allowlist diff visibly covers customer quick create only.
- Spec gap:
  - `FR-CM-05` mentions bacteria deposit / PCT / invalidation-specific fields; the allowlist diff clearly covers priority and conditional sections, but does not demonstrate the full matrix end-to-end.

## Status

- Final per-task status: `FAIL`
- Reason:
  - scope compliance is not met for the current frontend batch tied to this task ID, even though the allowlist subset materially advances the intended Batch 1 Cases UI behavior.
