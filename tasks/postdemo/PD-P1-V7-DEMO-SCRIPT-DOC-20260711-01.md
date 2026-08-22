# PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01

Status: PASS
Executor role: Business Demo Expert

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: medium
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-multi-lane-parallel-story`

## Exact Closure Slice

Create one standalone V7 presenter script that turns the approved design into ordered actions,
observable outcomes, four-state transitions, failure demonstrations, and recovery language.

## Explicit Non-Closure

Do not redefine the business contract or write operator setup commands; do not modify V6, product
code, tests, schema, seed, or customer source documents.

## Dependencies

- `docs/superpowers/specs/2026-07-11-postdemo-p1-v7-demo-docs-design.md`
- `docs/reviews/fpms_additional_gap_mitigation_close_audit_20260710.md`

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md`
- `tasks/postdemo/PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01.md`
- `artifacts/PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01/**`

## Verification Commands

- RED: target file must be absent before implementation.
- Lint: `git diff --check -- docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md tasks/postdemo/PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01.md`
- Test:

```bash
python3 -c 'from pathlib import Path; p=Path("docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md"); t=p.read_text(); ids=[f"V7-{i:02d}" for i in range(1,15)]; required=["P1七版演示客户有限公司","PD-P1-V7-LIVE","钱七老师","P1E2E-V7-LIVE","案件业务状态","法律状态","工作包/文件状态","费用节点状态","WIZARD","WORKPKG","OA","RECEIPT","CATALOG","DEADLINE","GRANT","要做的内容","输入的字段和值","点击的按钮","期望结果","主持人话术","失败演示","恢复方式","OA_OUT","CONFIRMED","错误案件","错误来源","后续OA","不自动生成草单","替代","已被替代","enrichment","不承诺自动提交"]; missing=[x for x in required+ids if x not in t]; assert not missing, missing; assert all(t.count(f"`{x}`")>=1 for x in ["WIZARD","WORKPKG","OA","RECEIPT","CATALOG","DEADLINE","GRANT"]); print("script_v7_structure=PASS steps=14")'
```

- Evidence/gate: initialize and run RED/lint/test with `evidence_gate.py`, finalize/validate, then
  `./scripts/task_validate.sh PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01`.

## Execution Ownership and Exact Evidence Commands

Implementer runs the following commands, creates scoped summary/diff/baselines, changes status only
to REVIEW, and stops:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py init PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01 --task-file tasks/postdemo/PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01.md --allowlist docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md --allowlist tasks/postdemo/PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01 red -- test -f docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01 lint -- git diff --check -- docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md tasks/postdemo/PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01 test -- python3 -c 'from pathlib import Path; t=Path("docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md").read_text(); ids=[f"V7-{i:02d}" for i in range(1,15)]; required=["P1七版演示客户有限公司","PD-P1-V7-LIVE","钱七老师","P1E2E-V7-LIVE","案件业务状态","法律状态","工作包/文件状态","费用节点状态","WIZARD","WORKPKG","OA","RECEIPT","CATALOG","DEADLINE","GRANT","要做的内容","输入的字段和值","点击的按钮","期望结果","主持人话术","失败演示","恢复方式","OA_OUT","CONFIRMED","错误案件","错误来源","后续OA","不自动生成草单","替代","已被替代","enrichment","不承诺自动提交","核心 GAP 路径不得使用 enrichment"]; missing=[x for x in required+ids if x not in t]; assert not missing, missing; print("script_v7_structure=PASS steps=14")'
```

Independent reviewer verifies scope/content, changes status to PASS, then runs:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py finalize PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01 --status PASS
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01
./scripts/task_validate.sh PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01
```

## Evidence Path

- `artifacts/PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01/**`

## Done Definition

The single target is standalone, executable by a presenter, structurally verified, independently
reviewed, scoped, evidence-valid, and task-gated.
