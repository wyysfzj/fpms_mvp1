# REPO-HIGH-DEVELOPMENT-HANDOFF-GUARDRAILS-20260713-01

Status: PASS
Executor role: Repository Governance Documentation Owner

## Design References

- `AGENTS.md`
- User-approved operating model: highest-capability reasoning for design freeze and high-risk audits; balanced/high reasoning for routine atomic development.
- Observed V8 Wave 0 execution evidence for manifest materialization, dependency review, scoped TDD, independent review, stall takeover, and gate closure.

## Story Shape Classification

- `shared_file_density`: low, with serialized exclusive ownership of `AGENTS.md`.
- `prereq_dependency_density`: low; V8 Wave 0 readiness is already independently closed.
- `be_fe_coupling`: none.
- `evidence_cost`: low; static semantic checks and scoped diff validation only.
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Add one durable repository-governance section to `AGENTS.md` that defines the `READY FOR HIGH DEVELOPMENT` handoff gate, separates highest-capability design/audit work from routine High atomic implementation, requires a minimal non-duplicative skill stack and narrow review context, defines automatic escalation triggers and an honest fallback when programmatic model switching is unavailable, and makes no-progress takeover observable and bounded.

## Explicit Non-Closure

Do not change product code, tests, schemas, migrations, manifests, V8 design/plan/catalog semantics, existing evidence, release behavior, customer decisions, model configuration, or Codex runtime capabilities. Do not claim that an agent can programmatically switch model tiers when its available tool interface has no model-selection control. Do not weaken atomicity, fail-closed behavior, dirty-baseline subtraction, independent review, SQLite serialization, evidence, task gates, or release gates.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `AGENTS.md`
- `tasks/repo/REPO-HIGH-DEVELOPMENT-HANDOFF-GUARDRAILS-20260713-01.md`
- `artifacts/REPO-HIGH-DEVELOPMENT-HANDOFF-GUARDRAILS-20260713-01/**`

No other source, test, task, manifest, design, plan, or shared-ownership file is authorized. Preserve and subtract the captured dirty baseline for `AGENTS.md`.

## Required Content

- A mechanical `READY FOR HIGH DEVELOPMENT` checklist that freezes exact task files, closure/non-closure, allowlists, dependencies, runbooks, verification, evidence paths, conflict-free waves, unresolved decision gates, and materialization/dependency preflight.
- Highest-capability/Ultra work limited to design freeze, unresolved legal/business or cross-module architecture, high-risk escalation, and Foundation/Full/Release close audits.
- High/balanced work as the default implementation lane for frozen atomic tasks through tracer TDD and scoped evidence.
- No broad source-document reanalysis by an implementation worker unless a genuine contract ambiguity is demonstrated.
- Minimal relevant skills only; overlapping workflow skills must not be loaded mechanically.
- Independent reviewer context limited to the task contract, baseline-subtracted diff, targeted results, and evidence unless a concrete ambiguity requires more.
- Shared files, migrations, SQLite-writing verification, repo-wide checks, and release gates remain serialized under existing rules.
- A two-observation stall rule based on allowlist-diff growth, artifact timestamps, and running verification; bounded takeover must preserve the same closure slice.
- Explicit escalation conditions and a handoff fallback when the runtime cannot switch model/reasoning tier programmatically; unaffected lanes continue safely.

## Verification Commands

- `rg -n "READY FOR HIGH DEVELOPMENT|Ultra|High implementation|programmatic model switching|escalation handoff|two consecutive observations|baseline-subtracted diff" AGENTS.md`
- A task-local Python semantic assertion over the required headings and phrases.
- `git diff --check -- AGENTS.md tasks/repo/REPO-HIGH-DEVELOPMENT-HANDOFF-GUARDRAILS-20260713-01.md`
- Baseline-subtracted patch scope must contain only the two authorized documentation paths.
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate REPO-HIGH-DEVELOPMENT-HANDOFF-GUARDRAILS-20260713-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- `./scripts/task_validate.sh REPO-HIGH-DEVELOPMENT-HANDOFF-GUARDRAILS-20260713-01`

## Evidence Path

- `artifacts/REPO-HIGH-DEVELOPMENT-HANDOFF-GUARDRAILS-20260713-01/**`

## Done Definition

The exact documentation slice is present without changing existing governance semantics; dirty baseline and a true baseline-subtracted patch exist; static semantic checks, scoped diff, scope audit, independent review, atomic evidence validation, and repository task gate all pass. Only then may this task be marked `PASS`.
