# FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-2-20260714-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Ultra Architect / Designer

## Story Shape Classification

- `shared_file_density`: high — later materialization updates several already-owned task
  files, but this design task owns only one new spec and its evidence.
- `prereq_dependency_density`: high — two narrow prerequisites remove accepted-test
  and evidence-role conflicts; the existing fee UI task already owns the callsite.
- `be_fe_coupling`: high — the batch includes backend HTTP contracts and one frontend
  adapter/existing-callsite dependency correction.
- `evidence_cost`: medium — design verification is structure/source/scope review only;
  product RED/GREEN remains in High.
- `chosen_runbook`: `P0-prereq-heavy-story`.

## Exact Closure Slice

Record one additive Ultra contract-freeze delta for the High blockers and deterministic
preflight ambiguity exposed after the first 2026-07-13 delta: lifecycle registry test
compatibility, filing XML lineage policy, generic attachment evidence intake, customer
decision-gate HTTP, fee-instruction HTTP, fee-preview frontend migration order,
fee-obligation detail read, first-ten-year annuity reduction and lifecycle-overlay public
contracts.

## Explicit Non-Closure

No product source, product test, schema, migration, endpoint, UI, existing V8 task
contract, batch manifest, materialization JSON, catalog, customer decision activation,
High implementation, repo-wide gate, commit or push. This task does not freeze any
unstarted fee rule or service merely because its original catalog wording is short.

## Dependencies

- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01` — PASS.
- The 43 effective Foundation task PASS records accepted before this delta.
- Blocker evidence under the eight affected task artifact families.
- Canonical V8 design and implementation plan dated 2026-07-12.

## Remaining Follow-Up Task IDs

- `FPMS-V8-ULTRA-CONTRACT-MATERIALIZATION-PLAN-2-20260714-01`
- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01`
- `FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01`
- `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`

## Allowed Files

- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-2-20260714-01.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `artifacts/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-2-20260714-01/**`

No existing task contract or product file is allowed in this closure.

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-2-20260714-01.md`
- `rg -n "^## (Purpose|Scope and precedence|Story Shape Classification|Approved approach|New atomic prerequisites|Frozen contract overrides|Dependency and runbook corrections|Non-closure|Acceptance)" docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `python3 -c 'from pathlib import Path; text = Path("docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md").read_text(); markers = ("RAW_ATTACHMENT", "POST /api/v1/system/decision-gates", "POST /api/v1/fees/obligations/{obligation_id}/instruction", "FILING_XML_DERIVATION_TYPE_MISMATCH", "get_fee_obligation", "validate_annuity_fee_reduction", "LifecycleOverlayQuery", "29 个 scoped", "202 个要求"); missing = [marker for marker in markers if marker not in text]; assert not missing, missing'`
- `for f in tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-2-20260714-01.md docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md; do out=$(git diff --no-index --check /dev/null "$f" 2>&1); rc=$?; [ "$rc" -eq 1 ] && [ -z "$out" ] || { printf '%s\n' "$out"; exit 1; }; done`
- `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-2-20260714-01`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-2-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-ULTRA-CONTRACT-FREEZE-DELTA-2-20260714-01/**`

## Done Definition

The spec freezes only the named blockers/preflight contract, creates exactly two
external prerequisite identities, records dependency/shared-file/runbook corrections,
defines exact callable/DTO/error/transaction/TDD boundaries, receives independent
architect review, passes scoped structure/diff/evidence/task gates, and changes no
product or existing task-contract file.
