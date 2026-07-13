# FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 8
Executor role: Frontend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

Execution-time recheck after Tasks59–62 exposed and closed the ordinary grant-mutation bypass:
all classifications remain `high` as recorded above and `chosen_runbook` remains
`P0-prereq-heavy-story`. The E2E stays one serial QA slice and gains no product ownership.

## Exact Closure Slice

新增并通过一个不依赖 enrichment 的真实用户路径 E2E，覆盖七个 GAP 的可观察结果。

## Explicit Non-Closure

不修改任何产品源码，不替代各原子 task 测试，不通过直接数据库注入跳过 UI/API，不使用
Playwright route mock/fulfill，不运行 enrichment seed，不把一个代表断言冒充整项覆盖。

## Dependencies

- Original Tasks 01–44: `PASS`
- Supplemental Tasks 48–62: `PASS`
- In particular: Task59 backend mutation gate, Task60 UI mutation gate, Task61 draft fixture
  alignment, and Task62 notice fixture alignment must remain independently gated.

## Remaining Follow-Up Task IDs

- 47

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-final-real-path.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01.md`
- `artifacts/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 通过真实登录/权限路径覆盖各既有权限。
- Status codes/errors: 按真实 API 合同断言 200/201 与 fail-closed 400/409/422；不得接受提前 close。
- Response envelope: 只消费已冻结的既有/扩展模型。
- SQLite: --workers=1；与其他 SQLite-writing tests 串行。
- Simplified Chinese UI: 所有被测用户可见文本必须为简体中文。

## Frozen Real-Path Scenario

One serial Playwright spec may use multiple uniquely suffixed cases. It must use real login and real
UI/API only, standard bootstrap seed, and an isolated SQLite database. It must record observable
checkpoints for all seven GAP rows:

1. Wizard/catalog: real template listing respects `page_size <= 100`; reference-only catalog rows
   remain visible but non-executable; executable OA/acceptance/grant aliases remain selectable.
2. Work-package reachability: filing and OA entry paths resolve/ensure a real package through their
   bodyless/keyed contracts without enrichment.
3. OA lifecycle: a confirmed-due OA_IN creates the correct package/task identity; OA_OUT does not
   prematurely close it; a valid same-case OA receipt archive closes/restores precisely; a later OA
   creates a distinct subsequent identity.
4. Receipt gates: wrong-case receipt follows Task14's frozen 400
   `OFFICIAL_WORK_PACKAGE_RECEIPT_CASE_MISMATCH`; a same-case receipt that does not attach the active
   OA source follows Task15's frozen 400 `OA_RECEIPT_ATTACHMENT_SOURCE_INVALID`. Neither failure
   mutates the active package/task.
5. Deadline carrier: create/read/update/wizard/impact-preview paths expose/persist structured due,
   source, and confirmation status, and the touched UI text is Simplified Chinese.
6. Grant lineage/replacement: confirmed grant notice creates sourced lineage without generic
   auto-draft; replacement creates a new notice/task and supersedes the old task; UI exposes the
   separate workflow/lineage values.
7. Grant mutation actionability: a superseded task produced through the public replacement path
   rejects direct draft reuse, batch client instruction, and notice generation with 409/no mutation;
   the new confirmed task can follow the normal client-PAY and draft-generation path. A fresh
   no-injection system has no public API for manufacturing a legacy grant task, so legacy behavior is
   cross-evidenced by independently gated Task59 rather than bypassing this task's no-DB-injection rule.

The spec must assert relevant positive 200/201 and negative 400/409/422 semantics. API setup is
allowed; direct DB injection and mocked transport are not.

## Verification Commands

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-final-real-path.spec.ts --workers=1`
- Scope: `git diff --check -- FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-final-real-path.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01/**`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
