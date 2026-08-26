# FPMS-DEMO-V6-UI-PARITY-STAGE03-LOCATOR-SYNC-20260826-08U

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["demo", "ui", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-STAGE03-LOCATOR-SYNC-20260826-08U.md
Chosen runbook: `P0-single-lane-story`

## Fixed References

- Approved design exact commit `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved implementation plan exact commit `80bd46829eaf5f798dda9422550a583c7fa12fde`.
- Accepted prerequisite Task 08T HEAD `11c1879858cc811e801bc9a4e067d4403f5d0898`.
- User-approved prerequisite: synchronize only the frozen Stage 03 locator contract with the
  already accepted Ordinal 04 visible UI before resuming Task 08.
- Active Task 08 is paused. Its disjoint uncommitted allowlist must remain byte-identical during
  Task 08U.

## Exact Closure Slice

Synchronize only Stage 03 `control` locator metadata in the canonical V6 parity testcase and its
executable contract with the accepted visible roles and labels.

## Exact Behavior

1. Filing completion time is combobox `人工递交时间`; filing note is textbox `递交备注`; and the
   final reviewed filing evidence is consumed by visible button `记录人工递交完成` on the filing
   preparation page.
2. Filing receipt evidence is combobox `回执文件`; receipt number is textbox `接收案件编号`;
   receipt time is combobox `接收时间`; and receiver is textbox `提交人` on the filing preparation
   page.
3. Acceptance, preliminary-examination, publication-notice, and substantive-examination evidence
   each use combobox `证据文件` on `/documents/:id`.
4. Focused executable assertions reject locator drift and prove every other Stage 03 field and row
   remains canonical. Values, classifications, routes, source selectors, normalization rules,
   outputs, and business semantics remain unchanged.

## Explicit Non-Closure

- No value, classification, normalization, route, source selector, output, assertion, business
  semantic, frontend, backend, schema, migration, seed, permission, lifecycle, fee, live browser,
  runner, receipt, or Task 08 behavior change.
- Do not modify or absorb the active Task 08 dirty baseline. Task 08 resumes only after Task 08U
  independent acceptance.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-STAGE03-LOCATOR-SYNC-20260826-08U.md`
- `FPMS_Automation_Skeleton_Pack/data/testcases/demo_v6_ui_parity_v1.json`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-STAGE03-LOCATOR-SYNC-20260826-08U/**`

## Verification Commands

```bash
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs
node --check FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs
git diff --check
```

RED is the focused contract rejecting the old Stage 03 visible locator metadata. GREEN is the exact
eleven-locator synchronization plus the Stage 03 non-control preservation assertion. Do not run
frontend, backend, live browser, broad, strict Playwright, or release gates in Task 08U.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-STAGE03-LOCATOR-SYNC-20260826-08U/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-STRICT-E2E-20260826-08`, resume after Task 08U acceptance.
- `FPMS-DEMO-V6-POST-STOP-CONSOLE-SECURITY-POSTDEMO`, remains deferred until after the demo.

## Done Definition

All eleven Stage 03 controls match the accepted visible UI, non-control Stage 03 contract bytes are
unchanged, the focused gates pass, active Task 08 bytes remain unchanged, and independent
zero-finding review plus atomic evidence accept the exact Task 08U range.

## Rollback

Run `git revert --no-edit <accepted-08U-range>`. Task 08 returns to its truthful Stage 03 locator RED.
