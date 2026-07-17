# AGENTS — FPMS Governance Kernel

This file is the proposed thin governance kernel. It is inactive until
`REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01` installs the reviewed kernel and manifest
and reaches terminal PASS. Until then, the repository's current root `AGENTS.md` controls.

## Authority and routing

Authority descends from current system/developer/user instructions, to this kernel, to the
[active manifest](docs/agents/manifest.json) and selected normative modules, to approved
designs/plans/exact task contracts, then to non-normative examples. Lower authority cannot
weaken higher authority. The manifest and [module guide](docs/agents/README.md) are mandatory
entry points for task start and close. Missing modules, unsafe or inconsistent selectors,
duplicate rules, unresolved references, owner conflicts, digest changes, or unexplained
governance conflicts fail closed for affected work.

### Rule GOV-BEHAVIOR-001 — Think first, stay simple, verify before claims

Surface assumptions, ambiguity, tradeoffs, and simpler alternatives. Stop for a genuine
contract ambiguity rather than guess. Implement only the minimum exact closure, match local
style, and avoid speculative abstractions, adjacent cleanup, renaming, or reformatting.
Every changed line must serve the task. Define observable success, use a test-first loop for
behavior, and never claim PASS, fixed, complete, or ready without fresh verification and
required evidence.

### Rule GOV-CUSTOMER-001 — Missing authority and customer decisions fail closed

Never invent or infer legal, lifecycle, deadline, official-fee, reduction, payment,
service-receivable, document/evidence lineage, permission/security, schema/migration,
customer-decision, or source-activation facts. Preserve the effective source and explicit
decision gate. Pause only affected lanes when ownership and dependencies remain disjoint.

### Rule GOV-RELEASE-001 — Independent task acceptance and release last

An implementer cannot approve its own work. PASS requires the exact task closure, current
baseline-subtracted scope, latest successful required results/logs, required independent
zero-finding review, task gate, and atomic evidence gate. Foundation, Full, Final, and
release/production close remain HIGH, serialized, and explicitly contracted. Product full
tests, broad Playwright, repo-wide checks, and the release gate run only at the named close
point; release is always last.

### Rule GOV-SKILLS-001 — Minimal precedence-ordered workflow

Repository and user rules remain authoritative. Use the smallest relevant skill stack in
this order: Karpathy discipline; the task-appropriate Superpowers workflow; relevant
engineering/domain skills; atomic evidence and verification. A contract-frozen task reuses
approved design, plan, classification, dependency graph, conflict map, and hashes. Do not
repeat brainstorming, source analysis, design, planning, or materialization unless a
concrete input, closure, dependency, owner, authority, or user request changed.

## Invariants routed to sole owners

Rule-Ref: GOV-MODULES-001
Rule-Ref: GOV-LIFECYCLE-001
Rule-Ref: GOV-FEE-001
Rule-Ref: GOV-LINEAGE-001
Rule-Ref: GOV-AUTH-001
Rule-Ref: GOV-DATA-001
Rule-Ref: GOV-SQLITE-001
Rule-Ref: GOV-API-UI-001
Rule-Ref: GOV-SCOPE-001
Rule-Ref: GOV-RISK-RUNTIME-001
Rule-Ref: GOV-RUNBOOK-001
Rule-Ref: GOV-LIVENESS-001
Rule-Ref: GOV-LINT-001
Rule-Ref: GOV-REPORT-001
Rule-Ref: GOV-MULTIAGENT-001
Rule-Ref: GOV-EVIDENCE-001
Rule-Ref: GOV-SOURCE-001
Rule-Ref: GOV-LEGACY-001

## Kernel operating boundary

- One active task owner has one exact task path, closure, non-closure, allowlist, and
  evidence bundle. Shared files, migrations, SQLite-writing tests, and broad verification
  are serialized.
- Repository risk LOW/MEDIUM/HIGH is distinct from runtime capability High/Ultra. Unknown
  or mixed risk takes the highest applicable tier; escalation requires a concrete blocker.
- New or changed APIs preserve status/response/permission semantics. New or changed visible
  UI text is Simplified Chinese; touching a page does not absorb unrelated legacy cleanup.
- A transport failure triggers durable-state reconciliation before retry. Resume from the
  first incomplete ordinal, permit at most one minimal-context replacement after the
  controlling liveness threshold, and never repeat completed durable steps.
- Governance digest changes require explicit independent adoption without recapturing or
  absorbing the task's original dirty baseline.

## Module routes

| Module | Load condition |
| --- | --- |
| `docs/agents/README.md` | Always |
| `docs/agents/execution.md` | Always |
| `docs/agents/evidence.md` | Always |
| `docs/agents/domain-safety.md` | HIGH or matching domain closure tags |
| `docs/agents/source-authority.md` | Source/customer/legal/fee/lineage review |
| `docs/agents/legacy-mvp1.md` | Matching legacy MVP1 task paths or tag |

If the manifest is missing, mismatched, staged, or not bound to the terminal PASS receipt
of its activation task, product work must not start.
