# FPMS-DEMO-V6-UI-PARITY-CASE-CONTACT-PROJECTION-20260826-08S

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["ui", "permission", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-CASE-CONTACT-PROJECTION-20260826-08S.md
Chosen runbook: `P0-single-lane-story`

## Fixed References

- Approved design exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved implementation plan exact commit `80bd46829eaf5f798dda9422550a583c7fa12fde`.
- Accepted Task 08R HEAD `04e2b19f2e7e882eb78eb3f6541fa50aca5755b1`.
- Frozen V6 Stage 01 output `same_case_primary_contact_and_first_applicant` in
  `FPMS_Automation_Skeleton_Pack/data/testcases/demo_v6_ui_parity_v1.json`.
- User approval: `` `批准 Task08S 案件详情主联系人最小投影边界，修复后恢复 Ordinal08` ``.
- Active Task 08 is paused at its truthful Stage 01 product-gap RED. Its disjoint uncommitted
  allowlist must remain byte-identical during Task 08S.

## Exact Closure Slice

On the existing case-detail page, read the current case customer's contacts through the existing
permission-protected client-contact GET and display contacts already marked `is_primary` beside the
existing first-applicant projection. This closes only the visible Stage 01 relationship projection.

## Exact Behavior

1. After the existing case GET resolves with `client_id`, the page calls the existing
   `getClientContacts(client_id)` public frontend API helper; it issues no mutation.
2. The page derives the display list only from returned contacts whose existing `is_primary` fact is
   true. It does not select, promote, deduplicate, or infer a primary contact.
3. The existing case-detail overview shows a Simplified-Chinese `客户主联系人` subsection with each
   matching contact's name, title, and email next to the existing applicant projection.
4. The existing case GET, client-contact endpoint, permission enforcement, response schemas, routes,
   case/contact writes, and all other case-detail behavior remain unchanged.
5. A focused contract test proves the existing GET helper path, read-only use, exact `is_primary`
   filter, and visible Chinese projection; typecheck and scoped lint remain green.

## Explicit Non-Closure

- No backend, endpoint, response, permission, schema, migration, model, seed, case/contact mutation,
  customer-selection rule, new error framework, loading framework, general case-party abstraction,
  other page, adjacent cleanup, or Stage 02–11 implementation.
- Do not modify any active Task 08 file or absorb its dirty baseline. Task 08 resumes only after 08S
  independent acceptance.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-CASE-CONTACT-PROJECTION-20260826-08S.md`
- `frontend/src/modules/cases/pages/CaseDetail.vue`
- `frontend/tests/demo-v6-case-contact-projection-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-CASE-CONTACT-PROJECTION-20260826-08S/**`

## Verification Commands

```bash
node frontend/tests/demo-v6-case-contact-projection-contract.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/modules/cases/pages/CaseDetail.vue \
  tests/demo-v6-case-contact-projection-contract.mjs)
git diff --check
```

RED is the focused contract missing the existing client-contact GET binding, exact primary filter,
and Chinese case-detail projection. GREEN is the focused contract, typecheck, scoped lint, and
scope check passing. Do not run broad or strict Playwright in Task 08S.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-CASE-CONTACT-PROJECTION-20260826-08S/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`, resume at Stage 01 after 08S acceptance.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`, remains deferred until after the demo.

## Done Definition

The case-detail overview displays only existing primary-contact facts for its current customer,
focused checks pass, active Task 08 bytes remain unchanged, and independent zero-finding review plus
atomic evidence accept the exact 08S range.

## Rollback

Run `git revert --no-edit <accepted-08S-range>`. Task 08 returns to its truthful Stage 01 RED.
