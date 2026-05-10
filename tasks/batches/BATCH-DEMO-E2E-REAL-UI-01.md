# BATCH-DEMO-E2E-REAL-UI-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: high
- chosen_runbook: P0-frontend-heavy-story

## Role

Lead / observable real-UI E2E tester.

## Exact Closure Slice

Run one observable real UI-interaction E2E happy path using the local FPMS frontend and backend. All business state-changing actions must be attempted through visible frontend interaction in the Codex in-app Browser:

1. Start or verify local backend and frontend services.
2. Open the real frontend in Browser and capture visible evidence.
3. Login through the UI.
4. Create one domestic invention case through UI controls only.
5. Fill required case fields through UI controls only.
6. Add/select client, applicant, and other required fields through UI controls only.
7. Satisfy any visible material-gate requirement through UI controls only if the product exposes that path.
8. Execute batch filing through UI controls only.
9. Verify through UI that case status changed appropriately and generated task / fee-draft related next-step UI is visible if supported.
10. Record unsupported or broken UI steps as BLOCKED with screenshots and exact reasons.

## Explicit Non-Closure

Do not:

- perform business setup or business mutations through API
- use headless Playwright as the primary proof
- call API-created records a true UI E2E
- modify backend or frontend product code
- modify Skeleton Pack YAML/JSON/schema/source assets
- claim full A+B wave completion
- claim `TC-B-005` or any deferred testcase complete
- store passwords, tokens, Authorization headers, or PII in artifacts

## Allowed Files

- `tasks/batches/BATCH-DEMO-E2E-REAL-UI-01.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-01 test /bin/zsh -lc 'test -f artifacts/BATCH-DEMO-E2E-REAL-UI-01/ui_e2e_report.md && test "$(find artifacts/BATCH-DEMO-E2E-REAL-UI-01/screenshots -type f -name "*.png" | wc -l | tr -d " ")" -ge 20'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-01 lint /bin/zsh -lc 'test -f tasks/batches/BATCH-DEMO-E2E-REAL-UI-01.md && test -f artifacts/BATCH-DEMO-E2E-REAL-UI-01/ui_e2e_report.md'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-01 secret_scan /bin/zsh -lc '! rg -n "admin123|Authorization: Bearer|access_token|eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+" artifacts/BATCH-DEMO-E2E-REAL-UI-01'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-REAL-UI-01 task_gate ./scripts/task_validate.sh BATCH-DEMO-E2E-REAL-UI-01
```

## Evidence Path

- `artifacts/BATCH-DEMO-E2E-REAL-UI-01/results.jsonl`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-01/summary.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-01/git/diff.patch`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-01/ui_e2e_report.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-01/browser_transcript.md`
- `artifacts/BATCH-DEMO-E2E-REAL-UI-01/screenshots/**`

## Remaining Follow-Up Task IDs

- `BATCH-DEMO-E2E-REAL-UI-01-FOLLOW-UP-CASE-MATERIALS-UI` if required material upload/registration is not exposed on the case-create or batch-filing UI.
- `BATCH-DEMO-E2E-REAL-UI-01-FOLLOW-UP-FEE-DRAFT-UI` if fee-draft generation cannot be completed through visible UI controls.

## Done Definition

PASS only if all in-scope business state changes are completed through visible UI interaction, screenshots and reports exist, no business mutation was done through API, and task gate passes.

If any required UI action is unavailable or broken, mark this task BLOCKED, not PASS.
