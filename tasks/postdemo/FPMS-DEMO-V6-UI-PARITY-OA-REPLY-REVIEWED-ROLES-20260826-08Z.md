# FPMS-DEMO-V6-UI-PARITY-OA-REPLY-REVIEWED-ROLES-20260826-08Z

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["ui", "lineage", "lifecycle", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OA-REPLY-REVIEWED-ROLES-20260826-08Z.md
Chosen runbook: `P0-single-lane-story`

## Fixed References

- Accepted pre-task HEAD `f931d001b225946ad341431599e6a64d69579e76`.
- Existing OA reply document selector and Stage 05 consumer are the only product seam.
- Active Task 08 has nine disjoint dirty files that must remain byte-identical.

## Exact Closure Slice

Adjust only `selectReviewedReplyDocumentOptions` so one eligible OA reply document produces one
deterministic candidate after its complete required reviewed attachment-role set is verified.

## Exact Behavior

1. A candidate document must be in the same case, have direction `OUT`, and have `reply_to_id`
   exactly equal to the current OA source document ID.
2. It must contain exactly one unambiguous attachment for each required role:
   `OA_STATEMENT_WORD`, `OA_STATEMENT_PDF`, and `OA_MODIFIED_CLAIMS`. Each required attachment is
   `APPROVED`, current, has a nonempty evidence version ID, and has a valid lowercase
   `sha256:` content hash. Non-final evidence is allowed only inside this reply selector.
3. Missing roles, pending or rejected evidence, noncurrent evidence, wrong case/source/direction,
   missing or invalid evidence identity/hash, duplicate required roles, and colliding required
   canonical identities reject the entire document.
4. Each eligible document yields exactly one deterministic representative option, never one row
   per required attachment. Stage 05 continues to reuse this selector.
5. `selectReviewedEvidenceOptions` remains final-only and the receipt selector remains unchanged.

## Explicit Non-Closure

- No component, backend, endpoint, request, response, type, permission, schema, database, generic
  selector framework, receipt-selector change, Stage 05 duplicate flow, Task 08 change, or adjacent
  cleanup.
- Do not run broad or Playwright suites when the focused Node contract dynamically executes the
  actual selector.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-OA-REPLY-REVIEWED-ROLES-20260826-08Z.md`
- `frontend/src/api/documents.ts`
- `frontend/tests/demo-v6-lifecycle-ui-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-OA-REPLY-REVIEWED-ROLES-20260826-08Z/**`

## Verification Commands

```bash
node frontend/tests/demo-v6-lifecycle-ui-contract.mjs
(cd frontend && npm run typecheck)
(cd frontend && npx eslint src/api/documents.ts tests/demo-v6-lifecycle-ui-contract.mjs)
git diff --check
```

RED is the real-shaped three-role reviewed non-final reply document returning no candidates.
GREEN is exactly one deterministic candidate plus the complete fail-closed negative matrix while
the generic selector remains final-only.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-OA-REPLY-REVIEWED-ROLES-20260826-08Z/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08` remains independently owned.

## Done Definition

The focused executable contract proves the exact required reviewed OA reply role set yields one
candidate and every specified drift rejects; focused gates pass, the Task 08 dirty baseline is
unchanged, and independent review plus atomic evidence accept the exact 08Z range.

## Rollback

Run `git revert --no-edit <accepted-08Z-range>`. The selector returns to final-only per-attachment
reply candidates.
