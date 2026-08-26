# FPMS-DEMO-V6-UI-PARITY-REVIEWED-RECEIPT-ELIGIBILITY-20260826-08V

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["ui", "lineage", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-REVIEWED-RECEIPT-ELIGIBILITY-20260826-08V.md
Chosen runbook: `P0-single-lane-story`

## Fixed References

- Accepted pre-task HEAD `36c8a2349b75184e20cd2ae0a10e720e3786f143`.
- User-approved boundary: existing reviewed receipt selector eligibility only.
- Active Task 08 has nine disjoint dirty files that must remain byte-identical.

## Exact Closure Slice

Adjust only the existing frontend reviewed-receipt evidence selector so a reviewed receipt whose
backend invariant is `RAW_ATTACHMENT` / `DRAFT` remains eligible without being marked final, while
preserving every lifecycle and grant selector's existing final-evidence requirement.

## Exact Behavior

1. `selectReviewedReceiptEvidenceOptions` accepts a same-case, current, `APPROVED` attachment with
   `evidence_version_id`, valid lowercase `sha256:` content hash, qualifying receipt role or receipt
   flags, even when `is_final=false`.
2. `selectReviewedEvidenceOptions`, used by lifecycle and grant flows, continues to require
   `is_final=true`.
3. Receipt selection rejects pending or rejected review, noncurrent attachment, wrong case,
   missing/invalid evidence identity or hash, ordinary nonreceipt attachment, and every duplicate
   canonical identity collision.
4. Existing backend, components, API request semantics, evidence state, and all other selectors
   remain unchanged.

## Explicit Non-Closure

- No backend, endpoint, permission, schema, migration, component, request, response, evidence-state,
  receipt-role expansion, generic selector framework, other selector broadening, Task 08 change, or
  adjacent cleanup.
- Do not run broad or strict Playwright gates.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-REVIEWED-RECEIPT-ELIGIBILITY-20260826-08V.md`
- `frontend/src/api/documents.ts`
- `frontend/tests/demo-v6-lifecycle-ui-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-REVIEWED-RECEIPT-ELIGIBILITY-20260826-08V/**`

## Verification Commands

```bash
node frontend/tests/demo-v6-lifecycle-ui-contract.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/api/documents.ts tests/demo-v6-lifecycle-ui-contract.mjs)
git diff --check
```

RED is the focused executable selector contract rejecting an otherwise reviewed non-final receipt.
GREEN preserves the strict lifecycle/grant selector while closing only reviewed receipt eligibility.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-REVIEWED-RECEIPT-ELIGIBILITY-20260826-08V/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08` resumes only after 08V acceptance.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO` remains deferred until after the demo.

## Done Definition

The receipt selector accepts the exact reviewed non-final receipt boundary, lifecycle/grant
eligibility remains strict, focused checks pass, all nine Task 08 dirty files remain byte-identical,
and independent review plus atomic evidence accept the exact 08V range.

## Rollback

Run `git revert --no-edit <accepted-08V-range>`. Task 08 returns to its prior receipt-selector RED.
