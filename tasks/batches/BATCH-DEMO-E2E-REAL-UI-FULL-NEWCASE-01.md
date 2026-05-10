# BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: high

## chosen_runbook

P0-frontend-heavy-story

## Exact Closure Slice

Run one TRUE observable full-case-lifecycle UI E2E using a brand-new domestic invention case created through visible frontend UI only.

The execution must:

1. Start or verify local backend/frontend services.
2. Open the real FPMS frontend in the Codex in-app Browser.
3. Login through UI if the session is not active.
4. Create a brand-new domestic invention case through UI only.
5. Record the generated case number in evidence.
6. Fill required case fields through UI only.
7. Add client/applicant/required parties through UI controls only.
8. Satisfy visible material-gate requirements through UI only if exposed.
9. Execute batch filing / filing submission through UI only.
10. Verify through UI that the case reaches post-filing receipt/status stage.
11. Register or observe official receipt / acceptance notice through UI if exposed.
12. Register OA / office action receipt through UI if exposed.
13. Register reply document through UI if exposed.
14. Verify OA reply task generation and completion/write-off state through UI if exposed.
15. Register grant notice through UI.
16. Verify grant-fee task appears in `/grant-fee/tasks`.
17. Generate `授权费通知函` through UI.
18. Record client payment instruction through UI if supported.
19. Generate grant-fee draft through UI if supported.
20. Open generated grant-fee draft through UI if linked.
21. Select official fee rows through visible UI controls.
22. Generate `官费清单` / pay-list through UI if supported.
23. Create bill from relevant locked draft/pay-list through UI if supported.
24. Verify bill detail through UI.
25. Verify case detail `账单与收款` tab shows linked bill.
26. Register collection/payment through visible UI.
27. Verify `回款与核销` page shows target payment/bill.
28. Perform visible offset/write-off path if supported.
29. Mark grant-fee task complete through UI if state allows.
30. Verify case reaches intended final grant/post-grant status through UI.
31. Generate or observe targeted annuity task through UI if supported.
32. Verify annuity task / fee draft / pay-list visibility through UI if supported.
33. Verify commission record / settlement visibility through UI if supported.
34. Capture screenshots after every major step.
35. Record unsupported, hidden, broken, or unreachable UI steps as BLOCKED with exact reason and screenshot.

All business state changes must be performed through visible UI interaction only: clicking, typing, selecting, submitting, confirming, filtering, and navigating. API use is limited to health/preflight or read-only diagnosis when UI behavior is ambiguous.

## Explicit Non-Closure

This task does not:

- reuse old case data, including `RUI202605100035`;
- use API to create the case, documents, fee drafts, bills, payments, offsets, annuity tasks, commission records, or any other business mutation;
- use headless Playwright as primary proof;
- modify backend or frontend product code;
- modify Skeleton Pack YAML/JSON/schema/source assets;
- claim full lifecycle PASS unless every required frontend-supported checkpoint is completed visibly;
- claim deferred testcase completion unless completed visibly;
- store passwords, tokens, Authorization headers, access tokens, or PII in artifacts.

## Allowed Files

- `tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01 test /bin/zsh -lc 'test -f artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/ui_full_lifecycle_e2e_report.md && test "$(find artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/screenshots -type f -name "*.png" | wc -l | tr -d " ")" -ge 15'

./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01 lint /bin/zsh -lc 'test -f tasks/batches/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01.md && test -f artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/ui_full_lifecycle_e2e_report.md'

./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01 secret_scan /bin/zsh -lc 'p1=admin"123"; p2="Authorization: ""Bearer"; p3=access"_token"; p4="ey""J[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"; ! rg -n "$p1|$p2|$p3|$p4" artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01'

./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01 task_gate ./scripts/task_validate.sh BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01
```

## Evidence Path

- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/results.jsonl`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/summary.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/git/diff.patch`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/ui_full_lifecycle_e2e_report.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/screenshots/**`
- optional: `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/browser_transcript.md`

## PASS Rules

Mark PASS only if:

- the case was newly created through visible UI;
- every frontend-supported in-scope lifecycle checkpoint was completed or verified through visible UI;
- every business mutation was UI-driven;
- screenshots exist for every major step;
- required evidence files exist;
- task gate passes;
- no API business mutation was used;
- explicit non-closure boundaries were respected;
- final grant/post-grant/financial state is visibly reached.

If any required lifecycle step remains unavailable, broken, hidden, or unreachable, mark final status BLOCKED and identify the next exact atomic follow-up task.

## Remaining Follow-Up Task IDs

- None if PASS.
- If BLOCKED, record the next exact atomic follow-up task ID in `artifacts/BATCH-DEMO-E2E-REAL-UI-FULL-NEWCASE-01/ui_full_lifecycle_e2e_report.md` and `summary.md`.
