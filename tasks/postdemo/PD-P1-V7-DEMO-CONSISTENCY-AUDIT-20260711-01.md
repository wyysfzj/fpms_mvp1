# PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01

Status: PASS
Executor role: Independent Reviewer

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Create one read-only consistency ledger proving that the three independently accepted V7 documents
share the frozen data/state vocabulary, cover all seven canonical GAP IDs, map script steps to
runbook checkpoints, respect the mixed real-path boundary, and leave the three protected V6 files
unchanged.

## Explicit Non-Closure

Do not edit any V7 or V6 document, product code, tests, schema, seed, or automation script. Findings
that require target changes return the owning task to REVIEW rather than being fixed here.

## Dependencies

- Tasks1–3 in `tasks/batches/PD-P1-V7-DEMO-DOCS-20260711-01.md`: PASS.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01.md`
- `artifacts/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01/**`

## Read-only Sources

- The three V7 target documents.
- The approved V7 planning spec and batch manifest.
- The three exact protected V6 paths listed in the batch manifest.

## Verification Commands

- Lint: `git diff --check -- tasks/postdemo/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01.md artifacts/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01/consistency_ledger.md`
- Test:

```bash
python3 -c 'from pathlib import Path; files=[Path("docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md"),Path("docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md"),Path("docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md")]; texts=[p.read_text() for p in files]; shared=["P1七版演示客户有限公司","PD-P1-V7-LIVE","钱七老师","P1E2E-V7-LIVE","案件业务状态","法律状态","工作包/文件状态","费用节点状态","WIZARD","WORKPKG","OA","RECEIPT","CATALOG","DEADLINE","GRANT","真实路径","enrichment"]; missing={str(p):[x for x in shared if x not in t] for p,t in zip(files,texts)}; assert not any(missing.values()), missing; ids=[f"V7-{i:02d}" for i in range(1,15)]; assert all(x in texts[1] and x in texts[2] for x in ids); assert "核心 GAP 路径不得使用 enrichment" in texts[1]; assert "核心 GAP 路径不得使用 enrichment" in texts[2]; print("v7_consistency=PASS docs=3 gaps=7 steps=14")'
test -z "$(git status --short -- docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md docs/postdemo/postdemo_p1_v6_ui_e2e_success_runbook_20260705.md)"
```
- Gate: finalize/validate atomic evidence and run
  `./scripts/task_validate.sh PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01`.

## Execution Ownership and Exact Evidence Commands

Independent audit executor initializes evidence, writes only the ledger, runs all recorded checks,
changes status only to REVIEW, and stops:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py init PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01 --task-file tasks/postdemo/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01.md --allowlist tasks/postdemo/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01.md --allowlist artifacts/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01/consistency_ledger.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01 lint -- git diff --check -- tasks/postdemo/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01.md artifacts/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01/consistency_ledger.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01 test -- python3 -c 'from pathlib import Path; files=[Path("docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md"),Path("docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md"),Path("docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md")]; texts=[p.read_text() for p in files]; shared=["P1七版演示客户有限公司","PD-P1-V7-LIVE","钱七老师","P1E2E-V7-LIVE","案件业务状态","法律状态","工作包/文件状态","费用节点状态","WIZARD","WORKPKG","OA","RECEIPT","CATALOG","DEADLINE","GRANT","真实路径","enrichment"]; missing={str(p):[x for x in shared if x not in t] for p,t in zip(files,texts)}; assert not any(missing.values()), missing; ids=[f"V7-{i:02d}" for i in range(1,15)]; assert all(x in texts[1] and x in texts[2] for x in ids); assert "核心 GAP 路径不得使用 enrichment" in texts[1] and "核心 GAP 路径不得使用 enrichment" in texts[2]; print("v7_consistency=PASS docs=3 gaps=7 steps=14")'
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01 v6_freeze -- /bin/zsh -lc 'test -z "$(git status --short -- docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md docs/postdemo/postdemo_p1_v6_ui_e2e_success_runbook_20260705.md)"'
```

Main-thread accepting reviewer verifies the read-only ledger, changes status to PASS, then runs:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py finalize PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01 --status PASS
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01
./scripts/task_validate.sh PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01
```

## Evidence Path

- `artifacts/PD-P1-V7-DEMO-CONSISTENCY-AUDIT-20260711-01/**`

## Done Definition

The read-only ledger maps every required consistency item to direct document evidence, reports no
residual mismatch, passes scoped evidence and task gate, and edits no target document.
