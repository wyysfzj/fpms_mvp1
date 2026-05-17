# AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01 — bad debt voucher visible ID cleanup

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Remove visible raw bad-debt voucher internal ID display from the bad debt panel.

This closes only:

1. `BadDebtPanel.vue` no longer renders `badDebtVoucher.id` as user-visible voucher text.
2. `BadDebtPanel.vue` displays a Chinese generated-state label for the voucher identity row.

## Explicit Non-Closure

This task does not:

- modify backend code, billing API wrappers/types, bill detail page wiring, permissions, response envelopes, or bad-debt action payloads.
- change mark/recover behavior, dialog fields, validation, status mapping, amount/date formatting, recovery table behavior, export, or print behavior.
- close raw-ID display issues outside `BadDebtPanel.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01.md`
- `frontend/src/modules/billing/components/BadDebtPanel.vue`
- `artifacts/AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/billing/components/BadDebtPanel.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "\\{\\{ badDebtVoucher\\.id \\}\\}" frontend/src/modules/billing/components/BadDebtPanel.vue && rg -n "formatVoucherDisplay|已生成" frontend/src/modules/billing/components/BadDebtPanel.vue'
./scripts/evidence_run.sh AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-BAD-DEBT-VOUCHER-ID-DISPLAY-01/baseline_external_files.txt`
