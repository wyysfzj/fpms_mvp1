# BATCH-DEMO-E2E-REAL-UI-FULL-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: high
- chosen_runbook: P0-frontend-heavy-story

## Role

Lead / observable real-UI full lifecycle E2E tester.

## Exact Closure Slice

Run one observable real UI-interaction full case lifecycle E2E continuation using the existing case `RUI202605100035`. Do not create a new case unless the existing case is not findable through the UI.

The execution must first inspect `FPMS_Automation_Skeleton_Pack` and existing task/docs to map intended lifecycle checkpoints, then execute the longest supported visible UI path for this case:

1. Start or verify local backend and frontend services.
2. Open the real frontend in the Codex in-app Browser and keep the session observable.
3. Login through UI if session is not active.
4. Locate existing case `RUI202605100035` through UI.
5. Verify current case status is `WAITING_RECEIPT` through UI.
6. Attempt post-filing receipt / acceptance-notice UI actions or observations if exposed.
7. Attempt examination / publication / substantive-examination / OA / reply-document UI path if exposed.
8. Attempt grant-stage, grant-fee, and final grant-status UI path if exposed.
9. Attempt financial lifecycle UI path: application fee draft, bill, collection/payment, and status verification if exposed.
10. Attempt post-grant annuity UI path if exposed.
11. Attempt commission lifecycle UI path if generated or reachable through UI.
12. Capture screenshots after every major step.
13. Record unsupported, hidden, broken, or unreachable UI steps as BLOCKED with screenshot and exact reason.

## Explicit Non-Closure

Do not:

- create a new case unless the existing case cannot be found through UI
- perform business setup or business mutations through API
- use headless Playwright as the primary proof
- call API-created records a true UI E2E
- modify backend or frontend product code
- modify Skeleton Pack YAML/JSON/schema/source assets
- claim full lifecycle PASS unless every required lifecycle checkpoint is completed visibly
- claim deferred testcase completion unless it was completed visibly
- store passwords, tokens, Authorization headers, access tokens, or PII in artifacts

## Allowed Files

- `tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-01.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-01 test /bin/zsh -lc 'test -f artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01/ui_full_lifecycle_e2e_report.md && test "$(find artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01/screenshots -type f -name "*.png" | wc -l | tr -d " ")" -ge 10'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-01 lint /bin/zsh -lc 'test -f tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-01.md && test -f artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01/ui_full_lifecycle_e2e_report.md'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-01 secret_scan /bin/zsh -lc '! rg -n "admin123|Authorization: Bearer|access_token|eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+" artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-01 task_gate ./scripts/task_validate.sh BATCH-DEMO-E2E-REAL-UI-FULL-01
```

## Evidence Path

- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01/results.jsonl`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01/summary.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01/git/diff.patch`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01/ui_full_lifecycle_e2e_report.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01/browser_transcript.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-01/screenshots/**`

## Remaining Follow-Up Task IDs

- `BATCH-DEMO-E2E-REAL-UI-FULL-01-FOLLOW-UP-RECEIPT-UI` if post-filing receipt or acceptance notice cannot be completed through visible UI.
- `BATCH-DEMO-E2E-REAL-UI-FULL-01-FOLLOW-UP-EXAM-OA-UI` if examination, OA receipt, or reply flow cannot be completed through visible UI.
- `BATCH-DEMO-E2E-REAL-UI-FULL-01-FOLLOW-UP-GRANT-UI` if grant or grant-fee flow cannot be completed through visible UI.
- `BATCH-DEMO-E2E-REAL-UI-FULL-01-FOLLOW-UP-FINANCE-UI` if fee draft, bill, collection, or payment flow cannot be completed through visible UI.
- `BATCH-DEMO-E2E-REAL-UI-FULL-01-FOLLOW-UP-ANNUITY-COMMISSION-UI` if annuity or commission lifecycle cannot be completed through visible UI.

## Done Definition

PASS only if every in-scope lifecycle checkpoint supported by the frontend was completed or verified through visible UI, every business mutation was UI-driven, required screenshots and reports exist, no business mutation was done through API, and task gate passes.

If any required full-lifecycle UI action is unavailable, broken, hidden, or unreachable, mark this task BLOCKED, not PASS.
