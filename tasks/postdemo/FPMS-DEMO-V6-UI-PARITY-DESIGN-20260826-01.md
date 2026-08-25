# FPMS-DEMO-V6-UI-PARITY-DESIGN-20260826-01

Status: READY FOR INDEPENDENT SPEC REVIEW
Risk: PROTECTED
Story type: design freeze only
Owner: design integrator

## Observable outcome

Freeze one reviewed design under which the existing automated V6 technical rehearsal remains
lane A, while a human presenter and another Codex account can each complete the same positive
11-stage business journey from an empty business database using only normal UI controls and the
same classified inputs. The design must expose rather than hide the current API-assisted gap.

## Non-goals

- No product, test, runner, API, schema, migration, seed, fee, lifecycle or release behavior
  changes in this design story.
- Do not relabel `SYNTHETIC_TEST_ONLY`, create customer-authorized inputs, or claim release.
- Do not absorb the existing candidate-document WIP or the dirty main-worktree baseline.

## Source and decision references

- User confirmation on 2026-08-26: HUMAN and CODEX are UI-only, use the same values, controls
  and results, and may not use direct business API/database bypasses; exact transcript and authority
  are recorded by `DEC-DEMO-V6-UI-PARITY-20260826`.
- `docs/postdemo/demo-lifecycle-customer-v6-runbook.md`
- `docs/superpowers/specs/2026-08-23-fpms-demo-v6-dual-track-fee-enrichment-design.md`
- `docs/superpowers/specs/2026-08-25-fpms-demo-v6-runtime-official-source-design.md`
- Current canonical and V6 Playwright journeys.

## Expected paths

- `docs/superpowers/specs/2026-08-26-fpms-demo-v6-ui-parity-design.md`
- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-DESIGN-20260826-01.md`
- `docs/product/v8/customer-decisions/2026-08-26-demo-v6-ui-parity.txt`
- `docs/product/v8/source-decision-registry.md`

No other path may change in this design story.

## Verification and acceptance

1. Exact two-path scope and synthetic fact boundary are explicit.
2. The 11-stage UI coverage table matches current frontend/backend evidence.
3. Direct business API/database/hidden-control bypasses are prohibited for HUMAN and CODEX.
4. Product changes are limited to observed UI gaps; no new business semantics are invented.
5. The customer decision is preserved byte-for-byte and indexed with version, hash, actor, scope,
   effective gate and rollback impact.
6. An independent High reviewer reviews the exact design commit and reports zero unresolved
   findings before user written-spec review.

## Rollback

Revert only the design-story commit. This story has no runtime or data effect.
