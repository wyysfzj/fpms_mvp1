# BATCH-DEMO-E2E-HAPPY-PATH-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Role

Lead / demo coordinator.

## Exact Closure Slice

Prepare a manual demo package for patent end-to-end happy path coverage using existing `FPMS_Automation_Skeleton_Pack` assets, and validate the package with targeted real-smoke automation.

This task closes only:

1. Create a demo data reference document with two run-scoped example data sets sourced from skeleton seed assets.
2. Create a detailed Markdown manual demo script for A wave new-case happy path and B wave OA happy path.
3. Record which happy-path testcase IDs are covered by the demo and which case is explicitly deferred.
4. Start backend/frontend services for local demo readiness when feasible.
5. Run targeted A/B happy-path automation smoke once against the local backend when feasible.
6. Create evidence artifacts for this demo preparation task.

## Explicit Non-Closure

Do not:

- implement new backend, frontend, or pytest handler behavior
- modify backend service/API/schema/model files
- modify frontend pages or routes
- modify `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/**`
- modify skeleton YAML/JSON/schema/Playwright assets
- claim deferred `TC-B-005` as implemented
- cover unhappy-path branches
- introduce new product rules or demo-only fake pass behavior

## In-Scope Testcase Coverage

### A Wave Happy Path

- `TC-A-001` 新案立案-最小必填
- `TC-A-002` 新案立案-完整字段
- `TC-A-011` 批量递交成功
- `TC-A-013` 申请费时限自动生成
- `TC-A-014` 时限基准与提醒
- `TC-A-015` 申请费草单生成
- `TC-A-017` 官费清单与缴费
- `TC-A-019` 申请费账单生成
- `TC-A-021` 客户付款与冲销
- `TC-A-023` 提成生成与可结算入口

### B Wave Happy Path

- `TC-B-001` OA来文登记
- `TC-B-002` 官方绝限覆盖
- `TC-B-004` OA答复任务生成
- `TC-B-006` OA答复去文
- `TC-B-008` 自动核销任务与状态恢复
- `TC-B-009` OA费用草单
- `TC-B-010` OA官方费清单
- `TC-B-011` OA账单与收款
- `TC-B-012` OA服务费计入提成
- `TC-B-013` 主界面修改 NeedReply/Deadline

Explicitly deferred from this demo closure:

- `TC-B-005` 内部准备任务 remains skeleton/deferred by `BATCH-B-WAVE-CLOSE-AUDIT-01`.

## Allowed Files

- `tasks/batches/BATCH-DEMO-E2E-HAPPY-PATH-01.md`
- `docs/demo/FPMS_DEMO_E2E_HAPPY_PATH.md`
- `docs/demo/FPMS_DEMO_E2E_DATA.md`
- `artifacts/BATCH-DEMO-E2E-HAPPY-PATH-01/**`

## Verification Commands

Documentation/evidence checks:

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-HAPPY-PATH-01 lint /bin/zsh -lc 'test -f docs/demo/FPMS_DEMO_E2E_HAPPY_PATH.md && test -f docs/demo/FPMS_DEMO_E2E_DATA.md && test -f tasks/batches/BATCH-DEMO-E2E-HAPPY-PATH-01.md'
./scripts/evidence_run.sh BATCH-DEMO-E2E-HAPPY-PATH-01 test /bin/zsh -lc 'rg -n "TC-A-001|TC-A-023|TC-B-001|TC-B-013|Demo Set 1|Demo Set 2|FPMS_DB_DSN=|TC-B-005" docs/demo/FPMS_DEMO_E2E_HAPPY_PATH.md docs/demo/FPMS_DEMO_E2E_DATA.md tasks/batches/BATCH-DEMO-E2E-HAPPY-PATH-01.md'
```

Targeted real smoke, from `FPMS_Automation_Skeleton_Pack/pytest_python`:

```bash
FPMS_API_URL=http://127.0.0.1:8000/api/v1 \
FPMS_USERNAME=admin \
FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" \
FPMS_RUN_ID=LOCAL-RUN-DEMO-A-HAPPY-001 \
FPMS_DB_DSN= \
pytest tests/test_wave_a.py -k "TC-A-001 or TC-A-002 or TC-A-011 or TC-A-013 or TC-A-014 or TC-A-015 or TC-A-017 or TC-A-019 or TC-A-021 or TC-A-023" -q
```

```bash
FPMS_API_URL=http://127.0.0.1:8000/api/v1 \
FPMS_USERNAME=admin \
FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" \
FPMS_RUN_ID=LOCAL-RUN-DEMO-B-HAPPY-001 \
FPMS_DB_DSN= \
pytest tests/test_wave_b.py -k "TC-B-001 or TC-B-002 or TC-B-004 or TC-B-006 or TC-B-008 or TC-B-009 or TC-B-010 or TC-B-011 or TC-B-012 or TC-B-013" -q
```

Task gate:

```bash
./scripts/evidence_run.sh BATCH-DEMO-E2E-HAPPY-PATH-01 task_gate ./scripts/task_validate.sh BATCH-DEMO-E2E-HAPPY-PATH-01
```

## Evidence Path

- `artifacts/BATCH-DEMO-E2E-HAPPY-PATH-01/results.jsonl`
- `artifacts/BATCH-DEMO-E2E-HAPPY-PATH-01/summary.md`
- `artifacts/BATCH-DEMO-E2E-HAPPY-PATH-01/git/diff.patch`
- `artifacts/BATCH-DEMO-E2E-HAPPY-PATH-01/baseline_allowlist.diff`
- `artifacts/BATCH-DEMO-E2E-HAPPY-PATH-01/baseline_external_files.txt`

## Remaining Follow-Up Task IDs

None for this demo package.

`TC-B-005` remains tracked by the B-wave deferred close decision and should not be folded into this demo task.
