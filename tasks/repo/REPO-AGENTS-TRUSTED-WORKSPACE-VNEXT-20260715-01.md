# REPO-AGENTS-TRUSTED-WORKSPACE-VNEXT-20260715-01

Status: PASS / INDEPENDENT GOVERNANCE REVIEW APPROVED 2026-07-15
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Repository Governance Maintainer / High worker
Risk tier: `HIGH` — authoritative `AGENTS.md` governance

## Design References

- `AGENTS.md` sections `0.3.1` through `0.3.5`
- User-approved Trusted-Workspace Evidence 1.1 direction dated 2026-07-15
- `docs/superpowers/specs/2026-07-15-fpms-atomic-evidence-bundle-v2-design.md` — historical, not accepted as implementation authority
- `artifacts/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01/review/round4_producer.md`
- `artifacts/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01/review/round4_consumer_gate.md`
- `artifacts/REPO-ATOMIC-EVIDENCE-BUNDLE-V2-DESIGN-20260715-01/review/round4_adversarial_checkpoint.md` — incomplete R4 axis; no final V2 approval

## Story Shape Classification

- `shared_file_density`: low — one authoritative governance file
- `prereq_dependency_density`: low — no product prerequisite
- `be_fe_coupling`: none
- `evidence_cost`: medium — deterministic semantic/scope checks plus independent governance review
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

## Exact Closure Slice

Add one `Trusted Workspace Evidence and Execution Boundary` section to `AGENTS.md` that:

1. trusts the local OS/kernel/filesystem, repository checkout, Git, Python and repository
   scripts as the development toolchain TCB unless a task explicitly requests a hostile-
   builder threat model;
2. limits ordinary evidence gates to detecting agent mistakes, incomplete/over-broad
   baseline-subtracted scope, missing untracked files, stale/forged result records and
   missing independent acceptance, without requiring defenses against malicious pre-init
   tool replacement or a privileged local operator;
3. explicitly preserves fail-closed legal/lifecycle/deadline, official-fee/reduction/
   payment, document/evidence lineage, permission/security, schema/migration, customer-
   decision, SQLite serialization and Foundation/Full/Release rules;
4. permits one persistent agent to receive later sequential task assignments while owning
   exactly one task at a time and preserving separate per-task closure/evidence/verdict;
5. requires one independent reviewer for ordinary HIGH implementation, permits one reviewer
   to cross-review a conflict-free wave with per-task verdicts, and requires two independent
   axes only for new unresolved cross-module architecture, Foundation/Full/Release close or
   an explicitly hostile-builder task. A user-approved, contract-frozen `AGENTS.md` amendment
   requires one independent governance reviewer; an unfrozen governance redesign requires two;
6. limits a governance remediation to at most three serialized prerequisite implementation
   tasks unless the user explicitly approves a larger chain;
7. permits only one minimal-context replacement after a confirmed worker/reviewer true
   stall; a second true stall stops that lane instead of spawning repeated replacements;
8. freezes the approved Evidence 1.1 repair as exactly three serialized repository tasks:
   producer scope, shared consumer/gate, and legacy activation. The incomplete Evidence
   Bundle V2 design remains historical and cannot start implementation.

## Explicit Non-Closure

No product source/test, legal/fee/document behavior, schema, migration, task status outside
this task, existing evidence/history, approved V8 catalog/manifest, release gate, global
skill, model setting, commit, push, reset, clean, stash or discard changes. This task does
not waive scope validation, dirty-baseline subtraction, task-local evidence, independent
acceptance, customer decisions, SQLite serialization or final release verification.

## Dependencies

- User approval of the Trusted-Workspace Evidence 1.1 direction — satisfied 2026-07-15.

## Remaining Follow-Up Task IDs

- `REPO-EVIDENCE-11-PRODUCER-SCOPE-20260715-01`
- `REPO-EVIDENCE-11-CONSUMER-GATE-20260715-01`
- `REPO-EVIDENCE-11-LEGACY-ACTIVATION-20260715-01`

## Allowed Files

- `tasks/repo/REPO-AGENTS-TRUSTED-WORKSPACE-VNEXT-20260715-01.md`
- `AGENTS.md`
- `artifacts/REPO-AGENTS-TRUSTED-WORKSPACE-VNEXT-20260715-01/**`

Capture and subtract the existing dirty `AGENTS.md` baseline. No other task, source, test,
artifact family or Git state is owned.

## Verification Commands

- Atomic task-shape check.
- Deterministic semantic validator for all eight closure rules and preserved iron rules.
- Baseline-subtracted scope check proving only `AGENTS.md` changed after task initialization.
- `git diff --check` on `AGENTS.md` and this task contract.
- Independent governance review with an explicit P0/P1/P2 verdict.
- Repository task gate and atomic evidence validation.

Product pytest, Ruff, migrations, frontend checks, Playwright, repo-wide checks and the
release gate are prohibited.

## Evidence Path

- `artifacts/REPO-AGENTS-TRUSTED-WORKSPACE-VNEXT-20260715-01/**`

## Done Definition

The Trusted-Workspace section is added once; all preserved product and release iron rules
remain explicit; dirty baseline and exact scope are proven; deterministic checks and one
independent governance verdict pass; repository task gate and atomic evidence validation
pass. Only then may the task report PASS and the three Evidence 1.1 tasks begin.
