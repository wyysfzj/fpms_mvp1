# AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01 - after-demo frontend display close audit

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: high
- chosen_runbook: P0-frontend-heavy-story

## Task Plan Classification

- shared_file_density: high
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: high
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Audit the completed after-demo frontend display cleanup batch and produce close evidence.

This closes only:

1. Verify all in-scope `AD-FE-*` task gates have required evidence.
2. Run final frontend lint/typecheck/build checks.
3. Run static scans for explicit user-facing `ID`/`UUID` wording and direct internal ID output.
4. Produce an item-to-slice ledger mapping prompt requirements to completed task IDs and residual debug-context exceptions.

## Explicit Non-Closure

This task does not:

- modify product source code, backend code, API contracts, route params, permissions, response envelopes, or UI behavior.
- create new feature/fix slices beyond audit evidence.
- mark unrelated pre-existing technical/debug contexts as product UI defects.

## Remaining Follow-Up Task IDs

- `None`

## Allowed Files

- `tasks/afterdemon/AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01.md`
- `artifacts/AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01 lint /bin/zsh -lc 'cd frontend && npx eslint src --max-warnings 0'
./scripts/evidence_run.sh AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01 ux_scan_explicit_id /bin/zsh -lc 'set -o pipefail; hits=$(rg -n "\\b(ID|UUID|uuid)\\b|代理人ID|申请人ID|Case ID|公文地址 ID|账单地址 ID|原案 ID|代理人 ID|撰写人 ID|内部代理人 ID|项目 ID|文档编号|回复来源文件 ID" frontend/src -g "*.vue" | rg -v "请求 ID|errorRequestId|requestId|ApiErrorBanner|PermissionDenied|Login" || true); test -z "$hits"'
./scripts/evidence_run.sh AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01 ux_scan_direct_id /bin/zsh -lc 'set -o pipefail; hits=$(rg -n "\\{\\{[^\\n]*(\\b[a-zA-Z0-9_]*id\\b|_id|\\.id)[^\\n]*\\}\\}|prop=\\"id\\" label=\\"编号\\"|prop=\\"id\\" :label" frontend/src -g "*.vue" | rg -v "format|formatMoney\\(income\\.total_paid|CaseReceiptsSummary|prop=\\"id\\" :label=\\"ZH\\.|getBillDisplay" || true); test -z "$hits"'
./scripts/evidence_run.sh AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01 task_gate ./scripts/task_validate.sh AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01
```

## Evidence Path

- `artifacts/AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01/results.jsonl`
- `artifacts/AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01/summary.md`
- `artifacts/AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01/git/diff.patch`
- `artifacts/AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01/baseline_allowlist.diff`
- `artifacts/AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01/baseline_external_files.txt`
