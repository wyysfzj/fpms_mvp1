# FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Ultra Governance Architect

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01.md`

## Story Shape Classification

- `shared_file_density`: low — exactly one authoritative governance file changes.
- `prereq_dependency_density`: low — the current Ultra controller must be PASS first.
- `be_fe_coupling`: none — no product behavior changes.
- `evidence_cost`: high — governance safety requires independent invariant review.
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: a fail-closed governance validator rejects a draft that deletes or
  weakens atomic scope, legal/fee/lineage/migration/security risk, PASS evidence, dirty
  baseline, SQLite serialization, independent review or the final release gate.
- GREEN expectation: the smallest additive/reconciliatory `AGENTS.md` change introduces
  explicit risk tiers and fast paths, removes repetitive planning/document duplication,
  and passes independent safety review with every named iron rule retained.

## Compact Governance Design

Chosen approach: add one authoritative risk-tier/fast-path section and surgically reconcile
only conflicting older clauses. LOW documentation/config work uses one compact task-level
design; MEDIUM frozen product work uses atomic TDD/evidence and per-task verdicts inside
efficient waves; HIGH legal status, official fee/money, evidence lineage, permissions,
security, schema/migration, irreversible data, customer decision and release work retains
the strictest fail-closed, serialization, independent review and gate requirements.

Rejected alternatives:

- Rewrite all of `AGENTS.md`: smaller final prose but excessive semantic-drift risk.
- Add a separate vNext supplement: faster edit but splits authority and creates precedence
  ambiguity.
- Keep every 5.0-era layer: safest mechanically but repeats frozen analysis and is the
  process-tax problem this task must close.

## Exact Closure Slice

Update the single authoritative `AGENTS.md` so future frozen V8 development is governed by
explicit LOW/MEDIUM/HIGH risk tiers, a no-repeat fast path and clear High-versus-Ultra
escalation boundaries while retaining atomic scope, fail-closed behavior, evidence,
independent acceptance, SQLite/shared-file serialization and the manifest-defined final
release gate.

## Explicit Non-Closure

No product source/test/schema/migration/API/UI, V8 task contract, approved spec/plan,
manifest, evidence from another task, customer decision, model setting, release gate,
commit or push is changed. This task does not authorize High product implementation and
does not relax any legal, fee, lineage, migration, security or irreversible-data rule.

## Dependencies

- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01` — PASS.
- User authorization to create and independently review `AGENTS.md vNext` before High.

## Remaining Follow-Up Task IDs

- `FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01` — first new delta-2
  external prerequisite when dependency-ready in the next High wave.
- `FPMS-V8-FOUNDATION-CLOSE-20260712-01` — eventual effective Foundation close after all
  individually owned implementation tasks pass.

## Allowed Files

- `tasks/postdemo/FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01.md`
- `AGENTS.md`
- `artifacts/FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01/**`

No product, task-contract, plan, manifest or other governance file is authorized. Preserve
and subtract the captured dirty baseline.

## Governance Safety Invariants

- One exact closure and allowlist per implementing agent remain mandatory.
- No concurrent shared-owner edits; migrations and SQLite-writing verification remain
  serialized.
- PASS still requires results, summary, scoped diff, dirty-baseline evidence when needed,
  scope validation, task gate and atomic evidence validation.
- An implementer cannot independently approve its own task. Batch review may be efficient
  but must retain an explicit per-task verdict.
- Legal status, official fee/rate/amount, evidence/document lineage, permissions/security,
  schema/migration, irreversible data, customer decision gates and Foundation/Full/Release
  close remain HIGH risk and fail closed.
- Full-repo checks and release gate remain restricted to their explicit manifest-defined
  close tasks; this governance task does not run them.
- High executes frozen contracts. Ultra is reserved for genuine contract ambiguity,
  high-risk design decisions and Foundation/Full/Release audits; no runtime model switch
  may be claimed when no switch control exists.

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01.md`
- `python3 artifacts/FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01/analysis/validate_agents_vnext.py`
- `python3 artifacts/FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01/analysis/validate_independent_review.py`
- `git diff --check -- AGENTS.md tasks/postdemo/FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01.md artifacts/FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01`
- `./scripts/task_validate.sh FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Product tests, Ruff, migration execution, frontend checks, Playwright, full-repo checks and
release gate are prohibited in this governance task.

## Evidence Path

- `artifacts/FPMS-AGENTS-VNEXT-GOVERNANCE-20260714-01/**`

## Done Definition

The risk tiers and fast path are explicit; frozen work no longer recreates broad design,
plan or controller layers without a demonstrated need; LOW/MEDIUM efficiency gains are
mechanically distinguishable from HIGH-risk iron rules; an independent reviewer confirms
fail-closed, scope, evidence, independent acceptance and release gate are not weakened;
dirty-baseline/scoped-diff evidence exists; task and atomic evidence gates pass; no
non-allowlisted or product file changes.
