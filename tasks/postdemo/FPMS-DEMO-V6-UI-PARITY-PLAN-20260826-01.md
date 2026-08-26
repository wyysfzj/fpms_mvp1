# FPMS-DEMO-V6-UI-PARITY-PLAN-20260826-01

Status: READY FOR INDEPENDENT PLAN REVIEW
Risk: PROTECTED
Story type: implementation-plan freeze only
Owner: plan integrator

## Observable outcome

Convert the independently approved UI-parity design commit `5d48d0a` into one executable,
test-first, ordinal implementation plan. The plan must preserve lane A and close lane B so a human
presenter and another Codex account can each complete the same V6 journey through normal UI only.

## Non-goals

- No product, test, runner, API, schema, migration, seed, fee, lifecycle, billing or release behavior
  changes in this plan story.
- No Docker redesign, general workflow engine, production/security expansion or customer-source
  activation.
- Do not absorb the release-document WIP worktree or dirty main-worktree baseline.

## Authority

- Approved design commit: `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Independent exact-commit design review: `APPROVED`.
- Customer written-spec acceptance preserved by
  `docs/product/v8/customer-decisions/2026-08-26-demo-v6-ui-parity-written-spec-acceptance.txt`.
- Registry decision: `DEC-DEMO-V6-UI-PARITY-20260826`.

## Expected paths

- `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-implementation.md`
- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-PLAN-20260826-01.md`
- `docs/product/v8/customer-decisions/2026-08-26-demo-v6-ui-parity-written-spec-acceptance.txt`
- `docs/product/v8/source-decision-registry.md`

No other path may change in this plan story.

## Verification and acceptance

1. Every implementation ordinal 00–09 has one exact task path, allowlist, RED, GREEN, focused gate,
   literal commit command, independent review and rollback. Read-only acceptance gates 10–11 make
   no repository commit and bind the already frozen ordinal-09 candidate SHA/tree.
2. HUMAN and CODEX business mutations remain UI-only; the observer is passive.
3. Existing A remains unchanged until the final named regression point.
4. The plan implements the versioned input/output contract, strict transitive-import gate, action /
   mutation ledgers and the complete 07–11 authority matrix.
5. Release remains a later, separately authorized last action.
6. An independent PROTECTED reviewer reports P0/P1/P2 = 0/0/0 on the exact plan commit.

## Rollback

Revert only this plan-story commit. It has no runtime or data effect.
