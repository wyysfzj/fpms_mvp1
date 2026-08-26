# FPMS-DEMO-V6-UI-PARITY-PREVIEW-AUDIT-20260826-08R

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["fee", "api", "ui", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-PREVIEW-AUDIT-20260826-08R.md
Chosen runbook: `P0-single-lane-story`

## Fixed References

- Approved design exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved implementation plan exact commit `80bd46829eaf5f798dda9422550a583c7fa12fde`.
- Accepted Ordinal 07 HEAD `50509d40bc4bbefbbb8eb2072c95e5af31af73d1`.
- User approval: `` `批准 Task08R Stage07 只读预览审计快照最小投影边界，修复后恢复 Ordinal 08` ``.
- Active Task 08 is paused at its truthful missing-projection RED; its disjoint uncommitted allowlist
  is outside this task and must remain byte-identical.

## Exact Closure Slice

Extend only the existing grant official-fee preview response with one V6 read-only audit snapshot
that proves, within the same clean SQLAlchemy session, that preview calculation changes no tracked
business identities or counts. Expose a compact Simplified-Chinese summary in the existing preview
dialog so the strict passive observer can bind the authoritative response without direct API/DB use.

## Exact Behavior

1. `GET /grant-fee-tasks/{task_id}/official-fee-preview` returns one versioned
   `read_only_audit_snapshot` containing sorted exact identity lists and counts before and after
   preview for: CaseActivityEvent; all three existing demo command carrier tables as one named
   group; FeeObligation; FeeObligationLine; FeeObligationDraftItemLink; FeeDraft; FeeItem; PayList;
   and GovPayment.
2. Both snapshots are captured in the same clean request transaction around the existing preview
   calculation. The response contains canonical before/after digests and `unchanged=true` only when
   every identity list and count is exactly equal. Any pending ORM new/dirty/deleted state or drift
   fails closed; the endpoint performs no flush, commit, insert, update, or delete.
3. Existing preview source, fee rows, amounts, rate/row/preview digests, permissions, status, and
   response semantics remain unchanged. No customer/source/fee fact is inferred.
4. The existing preview dialog shows only Chinese audit summary: tracked group count, total identity
   count, before/after digest, and “预览只读校验：一致（无业务写入）”. It does not add a raw-ID input
   or display raw identities to the presenter. Exact identities remain available only in the
   permission-protected response for passive strict verification.
5. Focused public-interface tests prove exact group coverage, stable ordering/digests, before=after,
   zero durable writes, malformed/drift rejection, and the visible Chinese summary.

## Explicit Non-Closure

- No new endpoint, database/schema/migration/model table, fee/rate/amount/calculation change,
  confirmation mutation change, permission expansion, lifecycle change, generic audit framework,
  production monitoring, security hardening, Stage 08–11 change, strict journey implementation,
  Runbook/docs, candidate, actor receipt, release, or adjacent cleanup.
- Do not modify any active Task 08 file or absorb its uncommitted baseline.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-PREVIEW-AUDIT-20260826-08R.md`
- `backend/app/modules/grant_fees/demo_official_fee.py`
- `backend/app/modules/grant_fees/schemas.py`
- `backend/tests/test_demo_v6_grant_official_fee.py`
- `frontend/src/api/grantFees.types.ts`
- `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `frontend/tests/demo-v6-grant-ui-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-PREVIEW-AUDIT-20260826-08R/**`

## Verification Commands

```bash
(cd backend && PYTHONPATH=. \
  /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python -m pytest -q \
  tests/test_demo_v6_grant_official_fee.py)
node frontend/tests/demo-v6-grant-ui-contract.mjs
(cd frontend && npm run typecheck)
(cd backend && /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/python -m ruff check \
  app/modules/grant_fees/demo_official_fee.py app/modules/grant_fees/schemas.py \
  tests/test_demo_v6_grant_official_fee.py)
(cd frontend && npx eslint src/api/grantFees.types.ts \
  src/modules/grantFees/pages/GrantFeeTaskList.vue)
git diff --check
```

RED is the focused endpoint/UI contract missing the audit snapshot and Chinese summary. GREEN proves
the snapshot is exact and read-only through the existing public preview interface. Run no broad or
strict Playwright gate in 08R.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-PREVIEW-AUDIT-20260826-08R/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`, resume from the absent-real-spec RED after 08R
  acceptance.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`, remains deferred until after the demo.

## Done Definition

The existing Stage 07 preview response and dialog truthfully expose exact same-transaction no-write
evidence, all focused checks pass, the active Task 08 bytes remain unchanged, and independent
zero-finding review plus atomic evidence accept the exact 08R range.

## Rollback

Run `git revert --no-edit <accepted-08R-range>`. Task 08 remains paused at its truthful RED.
