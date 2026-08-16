# FPMS-DEMO-ABC-DRAFT-LOCK-RECONCILE-20260816-01

Status: READY
Risk-Class: PROTECTED
Closure-Tags: ["demo", "frontend", "transport", "fee-draft"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-DRAFT-LOCK-RECONCILE-20260816-01.md

## Exact Closure Slice

Correct the ABC demo console's lock response handling. The existing lock endpoint returns only an
`OkOut`; after the durable lock succeeds, the frontend must read the authoritative draft detail and
must not replace the draft with the acknowledgement object.

## Explicit Non-Closure

No generic fee page rewrite, backend lock response change, lifecycle redesign, billing change,
production deployment, security or release gate.

## Allowed Files

- `frontend/src/modules/demo/demo.api.ts`
- `frontend/tests/demo-abc-contract.mjs`
- `artifacts/FPMS-DEMO-ABC-DRAFT-LOCK-RECONCILE-20260816-01/**`

## Verification Commands

1. RED proves the source contract rejects treating `OkOut` as a draft.
2. GREEN proves lock acknowledgement is followed by authoritative `GET /fees/drafts/{id}`.
3. Frontend typecheck and focused source contract pass.
4. Exact allowlist/diff checks pass; no broad or release gate runs.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-DRAFT-LOCK-RECONCILE-20260816-01/`

## Rollback

Revert the atomic product commit.

## Done definition

Target checks pass and the exact commit is ready for independent High review. The task remains
BLOCKED for acceptance until that review is recorded.
