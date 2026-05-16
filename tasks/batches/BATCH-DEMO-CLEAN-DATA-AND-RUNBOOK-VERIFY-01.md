# BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: high

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Clean local FPMS demo/test business transaction data while preserving configuration and base setup, then perform one observable browser validation against the verified full-case-lifecycle demo runbook v2.

This closure includes exactly:

1. Produce a cleanup keep list and delete plan before deleting data.
2. Delete demo/test business transaction rows from the local SQLite demo database.
3. Preserve configuration/base rows including users, roles, permissions, system parameters, task templates, document templates, template sources, fee rates, countries, seeded master data, grant-fee notice template configuration, annuity/grant-fee configuration, and commission rules/allocation/distribution configuration.
4. Record before/after business data counts and confirm commission rules remain.
5. Use the Codex in-app Browser to verify that the runbook v2 demo mainline remains reachable after cleanup, with visible UI interactions and screenshots.

## Explicit Non-Closure

This task does not:

- modify frontend or backend product code;
- modify Skeleton Pack YAML/JSON/schema/source assets;
- change schema or migrations;
- delete configuration/base setup when classification is ambiguous;
- delete commission rules, commission allocation configuration, or commission distribution rules;
- use API mutations for the browser validation stage;
- complete a full long-running customer demo chain end to end;
- repair any UI/product blocker discovered during validation.

## Allowed Files

- `tasks/batches/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01.md`
- `artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01 test /bin/zsh -lc 'test -f artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/cleanup_keep_list.md && test -f artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/cleanup_delete_plan.md && test -f artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/cleanup_result.md && test -f artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/runbook_browser_verify_report.md && test "$(find artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/screenshots -type f -name "*.png" | wc -l | tr -d " ")" -ge 5'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01 lint /bin/zsh -lc 'test -f tasks/batches/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01.md && test -f artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/summary.md'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01 secret_scan /bin/zsh -lc 'p1=admin"123"; p2="Authorization: ""Bearer"; p3=access"_token"; p4="ey""J[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"; ! rg -n "$p1|$p2|$p3|$p4" artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01'
```

```bash
./scripts/evidence_run.sh BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01 task_gate ./scripts/task_validate.sh BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01
```

## Evidence Path

- `artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/cleanup_keep_list.md`
- `artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/cleanup_delete_plan.md`
- `artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/cleanup_result.md`
- `artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/runbook_browser_verify_report.md`
- `artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/screenshots/**`
- `artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/results.jsonl`
- `artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/summary.md`
- `artifacts/BATCH-DEMO-CLEAN-DATA-AND-RUNBOOK-VERIFY-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- `tasks/frontend/cases/FE-CASE-DETAIL-DOCUMENT-GATE-VISIBLE-ERROR-01.md` if the non-blocking `材料门禁加载失败 / Network Error` warning on the case detail `往来文件` tab must be eliminated before customer demo.
- `tasks/frontend/cases/FE-CASE-CREATE-APPLICANT-VALIDATION-ZH-01.md` if the English create-case validation text must be normalized to Simplified Chinese before customer demo.
