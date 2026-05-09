# SKELE2E-HARNESS-COMMRULE-01 — Skeleton commission rule setup reuse

## Exact Closure Slice

Update only the FPMS Automation Skeleton Pack W0 commission setup helper so `TC-W0-CFG-006` reuses an existing `DS-CFG-COM-NORMAL-SERVICE` commission rule for the current `FPMS_RUN_ID` and re-enables it when the preceding W0 commission CRUD case has disabled it. This closes the `COMMISSION_RULE_CONFLICT` failure observed in the post-RUNID backend E2E rerun for `TC-W0-CFG-006`.

## Explicit Non-Closure

No product backend changes. No frontend changes. No database schema or migration changes. No change to product commission-rule conflict semantics. No changes to fee calc modes, config case setup, seed readiness expectations, case priority DB contract, batch material gate setup, granted-case setup, pay-list lifecycle, or browser-use runtime.

## Remaining Follow-Up Task IDs

- `SKELE2E-FEERATE-CALCMODE-01`
- `SKELE2E-HARNESS-CFGCASE-01`
- `SKELE2E-READINESS-CONTRACT-01`
- `SKELE2E-CASEPRIORITY-CONTRACT-01`
- `SKELE2E-BATCH-GATE-DATA-01`
- `SKELE2E-GRANTED-DATA-01`
- `SKELE2E-PAYLIST-CONTRACT-01`
- `SKELE2E-FE-STATIC-PAGEERROR-01`
- `SKELE2E-BROWSERUSE-RUNTIME-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. The task touches one W0 handler file and one focused W0 handler test file. |
| prereq_dependency_density | Medium. It removes one W0 setup conflict before remaining product/test-contract blockers can be isolated. |
| be_fe_coupling | Low. This is backend automation harness only and has no frontend surface. |
| evidence_cost | Medium. Requires focused TDD tests, lint, task gate, and a targeted W0 rerun when practical. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/e2e/SKELE2E-HARNESS-COMMRULE-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_commission_rule_handler.py`
- `artifacts/SKELE2E-HARNESS-COMMRULE-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m pytest -q tests/test_w0_commission_rule_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_commission_rule_handler.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/e2e/SKELE2E-HARNESS-COMMRULE-01.md`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate SKELE2E-HARNESS-COMMRULE-01`
- `./scripts/task_validate.sh SKELE2E-HARNESS-COMMRULE-01`

## Evidence Path

- `artifacts/SKELE2E-HARNESS-COMMRULE-01/`

## Done Definition

- Focused tests prove `TC-W0-CFG-006` can run after `TC-W0-CFG-005` in the same runtime without POSTing a duplicate commission rule.
- Focused tests prove a disabled existing rule is re-enabled before manual bill commission generation.
- Product commission-rule conflict validation remains untouched.
- Required evidence files exist and task gates pass.
