# FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 8
Executor role: Independent Reviewer / explorer

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

运行所有 task gates、全量检查和 manifest gate（先 exclude self），并产出七项 item-to-slice 最终 close audit。

## Explicit Non-Closure

不修复产品代码、不扩大七个 GAP、不把代表性测试当作全部覆盖、不在任何 residual gap
非 `None` 时宣告完成、不把 supplemental 写入冻结的 47-entry manifest。

## Dependencies

- Original Tasks 01–46: `PASS`
- Supplemental Tasks 48–70: `PASS`

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `docs/reviews/fpms_additional_gap_mitigation_close_audit_20260710.md`
- `backend/tests/test_addgap_final_close_ledger_contract.py`
- `tasks/additional_gaps/FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01.md`
- `artifacts/FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 审计所有函数参数权限注入；不变更权限注册表。
- Status codes/errors: 审计必须覆盖 200/201/204 body 语义及 400/401/403/404/409/422 合同。
- Response envelope: 审计既有响应包络一致性。
- SQLite: 串行运行全量 SQLite 测试；检查 migration/seed 兼容。
- Simplified Chinese UI: 审计触及页面全部为简体中文。

## Final Ledger Contract

- Exactly seven GAP rows; each maps required slices, original task IDs, relevant supplemental IDs,
  direct evidence, `residual gap = None`, and `close decision = covered`.
- A separate supplemental appendix lists Tasks48–70 without altering the frozen manifest and maps
  each to its parent slice, evidence files, independent review/task gate, residual, and decision.
- Program acceptance rows cover Tasks45, 46, and 47.
- The contract test independently checks task-file PASS status because `release_gate.sh` validates
  evidence but does not validate the task status field.
- Real-path verification remains the single frozen Task46 spec, not full heterogeneous Playwright scope.

## Verification Commands

- Contract test: `cd backend && .venv/bin/pytest -q tests/test_addgap_final_close_ledger_contract.py`
- Full backend: `cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q`
- Full frontend: `cd frontend && npm run lint && npm run typecheck && npm run build`
- Real path: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-final-real-path.spec.ts --workers=1`
- Program gate before self-finalize: `./scripts/release_gate.sh --manifest tasks/batches/FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01.md --exclude-task FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`
- After this task passes its own task gate, lead runs the same manifest gate without exclusion and stores output under the program artifact.
- Scope: `git diff --check -- docs/reviews/fpms_additional_gap_mitigation_close_audit_20260710.md backend/tests/test_addgap_final_close_ledger_contract.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01/**`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
