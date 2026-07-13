# FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 8
Executor role: Tester / monitor

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

`release_gate.sh` 支持 `--manifest <file>` 和可选 `--exclude-task ID` 验证列出的 task IDs，同时保留 no-arg 兼容行为。

## Explicit Non-Closure

不运行/修复产品测试，不改变 `task_validate.sh`，不伪造任一 task 证据。

## Dependencies

- Wave 0 planning gate（PASS）
- 必须在 `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01` 前执行

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `scripts/release_gate.sh`
- `backend/tests/test_addgap_manifest_release_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: N/A（本地 gate）。
- Status codes/errors: 进程 0 表示所选任务全部有效；任一缺失/FAIL/非法 manifest 非零。
- Response envelope: N/A。
- SQLite: 测试使用隔离临时 artifact fixtures，不访问共享 SQLite。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_manifest_release_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_addgap_manifest_release_gate.py && .venv/bin/ruff format tests/test_addgap_manifest_release_gate.py && .venv/bin/ruff check tests/test_addgap_manifest_release_gate.py`
- Scope: `git diff --check -- scripts/release_gate.sh backend/tests/test_addgap_manifest_release_gate.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01/**`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
