# FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-2-20260714-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Ultra Architect / Planner

## Story Shape Classification

- `shared_file_density`: high — the later High tasks contain lifecycle, document,
  fee-API and overlay shared-file chains; this plan owns only itself and one plan doc.
- `prereq_dependency_density`: high — two external prerequisites and twenty-two contract
  overrides must compose with the accepted delta-1 overlay without a close bypass.
- `be_fe_coupling`: high — strict fee/overlay backend contracts must reach existing
  frontend adapters and exact UI tasks without duplicate ownership.
- `evidence_cost`: high — deterministic parent/delta hashes, graph closure, independent
  review and atomic gates remain mandatory.
- `chosen_runbook`: `P0-prereq-heavy-story`.

## Exact Closure Slice

Create one reviewed implementation plan and explicit 25-task-file contract-materialization
batch for the approved Ultra delta-2, preserving the immutable V8 baseline and accepted
delta-1 while making the two new prerequisites mandatory before effective Foundation
close.

## Explicit Non-Closure

No existing V8 task-contract edit, product source/test/schema/migration/API/UI change,
customer decision activation, High implementation, immutable baseline/delta-1 rewrite,
repo-wide check, release gate, commit or push.

## Dependencies

- `FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-2-20260714-01` — PASS.
- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01` — PASS.

## Remaining Follow-Up Task IDs

- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01`

## Allowed Files

- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-2-20260714-01.md`
- `docs/superpowers/plans/2026-07-14-fpms-v8-ultra-contract-materialization-2.md`
- `artifacts/FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-2-20260714-01/**`

No existing product/task contract or shared ownership file is authorized in this closure.

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-2-20260714-01.md`
- `rg -n "^# .*Implementation Plan|^> \*\*For agentic workers|^## Story Shape Classification|^## Explicit batch manifest|^## Wave order|^## Delta-2 overlay contract|^## Shared ownership and verification|^## Done definition" docs/superpowers/plans/2026-07-14-fpms-v8-ultra-contract-materialization-2.md`
- `python3 artifacts/FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-2-20260714-01/analysis/validate_plan.py`
- `for f in tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-2-20260714-01.md docs/superpowers/plans/2026-07-14-fpms-v8-ultra-contract-materialization-2.md; do out=$(git diff --no-index --check /dev/null "$f" 2>&1); rc=$?; [ "$rc" -eq 1 ] && [ -z "$out" ] || { printf '%s\n' "$out"; exit 1; }; done`
- `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-2-20260714-01`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-2-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-2-20260714-01/**`

## Done Definition

The plan names exactly twenty-five agent-owned task-file paths, assigns one closure and
allowlist per row, freezes two new prerequisites and twenty-two non-duplicating contract
overrides, defines deterministic delta-2 overlay/controller validation, preserves
283/197/86 plus accepted delta-1 history, proves effective Foundation 202 and graph 288,
receives independent plan review, and passes scoped evidence/task gates without product
or existing-task edits.
