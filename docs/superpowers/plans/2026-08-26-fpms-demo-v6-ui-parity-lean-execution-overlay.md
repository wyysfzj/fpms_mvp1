# FPMS Demo V6 UI 等价精简执行 Overlay

Status: ACTIVE

## Binding

- Parent implementation plan: `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-implementation.md`
- Parent exact commit: `80bd46829eaf5f798dda9422550a583c7fa12fde`
- User approval: `` `批准记录 task-scoped 精简执行 overlay` ``
- Scope: only Ordinal 00–11 of the bound parent plan.

This overlay narrows execution ceremony only. It does not change the approved design, plan,
task closures, ordinal order, candidate identity, acceptance criteria, or release boundary.

## Preserved Invariants

The following remain fully authoritative and cannot be weakened by this overlay:

- authority, fact, security, fee, lifecycle, customer-decision, lineage, and source boundaries;
- test-first RED/GREEN behavior work and each task's exact file allowlist;
- required evidence and independent P0/P1 acceptance;
- immutable Task 09 candidate binding for Ordinals 10–11;
- release-last and all explicit release/production non-closures.

## Lean Execution Rules

1. Freeze the approved design and parent plan. Do not repeat brainstorming, architecture,
   source analysis, planning, or review unless a reproducible RED proves the exact contract
   impossible to implement.
2. Execute one ordinal at a time using this fixed loop:
   read only that task slice; run its named RED; repair the first failing owner; obtain GREEN;
   run the mechanical precheck; obtain one independent diff review; commit; advance.
3. Run the mechanical precheck before human review:
   verify the exact file allowlist and paths; verify shell working directory and dry-run command
   shape where applicable; run `git diff --check`; verify task, commit, and evidence fields.
4. Review has one primary pass and at most one findings-only remediation pass. A third review is
   allowed only when new P0/P1 evidence appears. P2 style observations and adjacent cleanup do
   not block the demo and are recorded separately.
5. If 30 minutes pass without observable RED-to-GREEN progress, stop the ordinal and report only:
   first failing command, root cause, minimum repair boundary, and any additional authority needed.
   Do not respond by adding abstractions or expanding scope.
6. Test at the level assigned by the parent plan: Ordinals 00–07 run focused gates only;
   Ordinal 08 runs the strict UI journey; Ordinal 11 runs full A2, strict2, and fresh-clone close.
   Do not repeat broad suites at intermediate ordinals.
7. Emit one compact status receipt per ordinal:
   `Ordinal / RED / changed files / GREEN / independent review / commit / next`.
8. Do not promote these rules to global governance before the customer demo. Any promotion is a
   separate post-demo retrospective and governance task with its own approval.

## Stop Conditions

Stop the affected ordinal when any of the following occurs:

- work would exceed its exact closure or file allowlist;
- a speculative abstraction, general framework, or adjacent cleanup is proposed;
- a third review is requested without new P0/P1 evidence;
- a broad gate is run at an ordinal that does not own it;
- any repository byte change is proposed after the Task 09 candidate is frozen.

## Completion and Rollback

This overlay is active when this document and its task card are committed together and their
binding fields pass the listed mechanical checks. It authorizes no product implementation by
itself; execution still requires explicit approval of the parent implementation plan.

Rollback is `git revert --no-edit <overlay-commit-sha>`. Reverting the overlay leaves the parent
plan and all previously approved bytes unchanged.
