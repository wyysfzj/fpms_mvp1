# FPMS P1 V7 Demo Documents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce three standalone, mutually consistent V7 demo documents that accurately expose the completed seven-GAP mitigation through a mixed real-path customer demonstration.

**Architecture:** The design document owns the canonical business contract, the script owns presenter actions and observable transitions, and the runbook owns environment/readiness/evidence controls. Each file is an independent atomic documentation task; V6 remains historical and unchanged.

**Tech Stack:** Markdown, repository evidence scripts, Python standard-library structural checks, Git scoped diff checks.

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: medium
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-multi-lane-parallel-story`

The planning spec is the complete frozen contract shared by the three parallel authoring tasks.
Task 1's output is not a prerequisite input to Tasks 2 or 3.

## Evidence ownership

Each task section contains fully expanded commands. The implementer runs init, expected RED, lint,
and test, produces scoped evidence, changes status only to REVIEW, and stops. An independent
reviewer verifies the target, changes status to PASS, runs `finalize --status PASS`, restores a
target/task-only baseline-subtracted diff if needed, then runs validate and task gate. PASS requires
`results.jsonl`, `summary.md`, scoped `git/diff.patch`, and dirty-baseline files.

---

### Task 1: V7 lifecycle demo design

**Files:**
- Create: `docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md`
- Task: `tasks/postdemo/PD-P1-V7-DEMO-DESIGN-DOC-20260711-01.md`
- Evidence: `artifacts/PD-P1-V7-DEMO-DESIGN-DOC-20260711-01/**`

- [ ] Preserve RED evidence that the target file does not exist.
- [ ] Write the standalone canonical V7 design using the approved design spec and final GAP close audit.
- [ ] Include one-case/four-state model, mixed real-path boundary, seven-capability matrix, fail-closed semantics, non-goals, and success criteria.
- [ ] Run the exact structural command frozen in the task file; it requires all seven canonical IDs,
  shared V7 data names, four state dimensions, mixed real-path rules, and protected V6 paths.
- [ ] Produce scoped evidence and hand off for independent review.

**Exact commands:**

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py init PD-P1-V7-DEMO-DESIGN-DOC-20260711-01 --task-file tasks/postdemo/PD-P1-V7-DEMO-DESIGN-DOC-20260711-01.md --allowlist docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md --allowlist tasks/postdemo/PD-P1-V7-DEMO-DESIGN-DOC-20260711-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-DESIGN-DOC-20260711-01 red -- test -f docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-DESIGN-DOC-20260711-01 lint -- git diff --check -- docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md tasks/postdemo/PD-P1-V7-DEMO-DESIGN-DOC-20260711-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-DESIGN-DOC-20260711-01 test -- python3 -c 'from pathlib import Path; t=Path("docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md").read_text(); required=["P1七版演示客户有限公司","PD-P1-V7-LIVE","钱七老师","P1E2E-V7-LIVE","案件业务状态","法律状态","工作包/文件状态","费用节点状态","WIZARD","WORKPKG","OA","RECEIPT","CATALOG","DEADLINE","GRANT","真实路径","enrichment","OA_OUT","CONFIRMED","来源已确认","已被替代","不自动生成草单","同案","正确来源","不承诺自动提交","postdemo_p1_lifecycle_demo_design_20260704.md","postdemo_p1_lifecycle_demo_script_20260704.md","postdemo_p1_v6_ui_e2e_success_runbook_20260705.md"]; missing=[x for x in required if x not in t]; assert not missing, missing; print("design_v7_structure=PASS")'
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py finalize PD-P1-V7-DEMO-DESIGN-DOC-20260711-01 --status PASS
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate PD-P1-V7-DEMO-DESIGN-DOC-20260711-01
./scripts/task_validate.sh PD-P1-V7-DEMO-DESIGN-DOC-20260711-01
```

### Task 2: V7 detailed presenter script

**Files:**
- Create: `docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md`
- Task: `tasks/postdemo/PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01.md`
- Evidence: `artifacts/PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01/**`

- [ ] Preserve RED evidence that the target file does not exist.
- [ ] Write a standalone sequence from UI customer/case creation through core GAP real paths and the limited fee/letter/annuity enrichment branch.
- [ ] Give every step input/action/result/four-state/presenter/failure/recovery fields.
- [ ] Demonstrate OA open-until-receipt, receipt ownership failures, later OA identity, explicit deadlines, grant no-auto-draft, replacement, and superseded fail-closed behavior.
- [ ] Run the exact structural command frozen in the task file; it requires all seven canonical IDs,
  the shared V7 data names, step template, core real paths, failures, recovery, and boundaries.
- [ ] Produce scoped evidence and hand off for independent review.

**Exact commands:**

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py init PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01 --task-file tasks/postdemo/PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01.md --allowlist docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md --allowlist tasks/postdemo/PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01 red -- test -f docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01 lint -- git diff --check -- docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md tasks/postdemo/PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01 test -- python3 -c 'from pathlib import Path; t=Path("docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md").read_text(); ids=[f"V7-{i:02d}" for i in range(1,15)]; required=["P1七版演示客户有限公司","PD-P1-V7-LIVE","钱七老师","P1E2E-V7-LIVE","案件业务状态","法律状态","工作包/文件状态","费用节点状态","WIZARD","WORKPKG","OA","RECEIPT","CATALOG","DEADLINE","GRANT","要做的内容","输入的字段和值","点击的按钮","期望结果","主持人话术","失败演示","恢复方式","OA_OUT","CONFIRMED","错误案件","错误来源","后续OA","不自动生成草单","替代","已被替代","enrichment","不承诺自动提交","核心 GAP 路径不得使用 enrichment"]; missing=[x for x in required+ids if x not in t]; assert not missing, missing; print("script_v7_structure=PASS steps=14")'
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py finalize PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01 --status PASS
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01
./scripts/task_validate.sh PD-P1-V7-DEMO-SCRIPT-DOC-20260711-01
```

### Task 3: V7 UI E2E success runbook

**Files:**
- Create: `docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md`
- Task: `tasks/postdemo/PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01.md`
- Evidence: `artifacts/PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01/**`

- [ ] Preserve RED evidence that the target file does not exist.
- [ ] Define environment, permission, cleanup, data isolation, and mixed real-path preparation.
- [ ] Freeze preflight and ordered checkpoints matching the V7 script.
- [ ] Add stop/recovery rules for fail-closed deadline, receipt, catalog, and grant-lineage outcomes.
- [ ] Require post-run evidence, cleanup, and a final readiness checklist.
- [ ] Run the exact structural command frozen in the task file; it requires all seven canonical IDs,
  the shared V7 data names, preflight, permissions, cleanup, checkpoints, stop/recovery, and evidence.
- [ ] Produce scoped evidence and hand off for independent review.

**Exact commands:**

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py init PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01 --task-file tasks/postdemo/PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01.md --allowlist docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md --allowlist tasks/postdemo/PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01 red -- test -f docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01 lint -- git diff --check -- docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md tasks/postdemo/PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01 test -- python3 -c 'from pathlib import Path; t=Path("docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md").read_text(); ids=[f"V7-{i:02d}" for i in range(1,15)]; required=["P1七版演示客户有限公司","PD-P1-V7-LIVE","钱七老师","P1E2E-V7-LIVE","案件业务状态","法律状态","工作包/文件状态","费用节点状态","WIZARD","WORKPKG","OA","RECEIPT","CATALOG","DEADLINE","GRANT","Preflight","权限","cleanup","明确 allowlist","真实路径","禁止 route mock","禁止数据库注入","enrichment","停止条件","恢复","Evidence","演示后清理","READY","OA_OUT","CONFIRMED","已被替代","核心 GAP 路径不得使用 enrichment"]; missing=[x for x in required+ids if x not in t]; assert not missing, missing; print("runbook_v7_structure=PASS checkpoints=14")'
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py finalize PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01 --status PASS
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01
./scripts/task_validate.sh PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01
```

### Task 4: Final consistency audit

**Files:**
- Task: `tasks/postdemo/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01.md`
- Create: `artifacts/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01/consistency_ledger.md`
- Evidence: `artifacts/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01/**`

- [ ] Initialize Task4 evidence after Tasks1–3 PASS.
- [ ] Write a read-only ledger mapping shared names, four state dimensions, seven canonical IDs,
  every script step/checkpoint pair, mixed real-path boundaries, and residual mismatch.
- [ ] Run the exact Python structural command frozen in Task4.
- [ ] Verify these protected paths remain clean with `git status --short --`:
  `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`,
  `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`, and
  `docs/postdemo/postdemo_p1_v6_ui_e2e_success_runbook_20260705.md`.
- [ ] Run Task4 lint/test, finalize/validate evidence, and
  `./scripts/task_validate.sh PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01`.

**Exact commands:**

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py init PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01 --task-file tasks/postdemo/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01.md --allowlist tasks/postdemo/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01.md --allowlist artifacts/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01/consistency_ledger.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01 lint -- git diff --check -- tasks/postdemo/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01.md artifacts/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01/consistency_ledger.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01 test -- python3 -c 'from pathlib import Path; files=[Path("docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md"),Path("docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md"),Path("docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md")]; texts=[p.read_text() for p in files]; shared=["P1七版演示客户有限公司","PD-P1-V7-LIVE","钱七老师","P1E2E-V7-LIVE","案件业务状态","法律状态","工作包/文件状态","费用节点状态","WIZARD","WORKPKG","OA","RECEIPT","CATALOG","DEADLINE","GRANT","真实路径","enrichment"]; missing={str(p):[x for x in shared if x not in t] for p,t in zip(files,texts)}; assert not any(missing.values()), missing; ids=[f"V7-{i:02d}" for i in range(1,15)]; assert all(x in texts[1] and x in texts[2] for x in ids); assert "核心 GAP 路径不得使用 enrichment" in texts[1] and "核心 GAP 路径不得使用 enrichment" in texts[2]; print("v7_consistency=PASS docs=3 gaps=7 steps=14")'
test -z "$(git status --short -- docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md docs/postdemo/postdemo_p1_v6_ui_e2e_success_runbook_20260705.md)"
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py finalize PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01 --status PASS
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01
./scripts/task_validate.sh PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01
```

No commit is part of this execution unless the user separately authorizes it.
