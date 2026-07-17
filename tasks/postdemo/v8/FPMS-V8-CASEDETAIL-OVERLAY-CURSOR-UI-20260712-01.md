# FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-14 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `16. Wave 7 — lifecycle overlay and centered UI`
Catalog ordinal: `274`
Executor role: Frontend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `812`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: high
- `evidence_cost`: medium
- `chosen_runbook`: `P0-frontend-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-UI`

- RED expectation: Targeted Playwright fails on the frozen multi-page cursor, milestone-only append/deduplication or complete decision-gate snapshot behavior.
- GREEN expectation: Targeted Playwright, exact-file ESLint and serialized `FE-TYPE` pass without frontend state inference.

## Exact Closure Slice

Load more using the first revision, next cursor and deduplication; never claim complete history while `has_more`.

## Ultra Contract Freeze — 2026-07-14 (delta-2)

This section is authoritative for High implementation. It freezes only the existing
cursor/load-more closure on top of the accepted three-lane layout and gates/warnings
presentation. It does not add another page capability or redefine the server overlay.

### Frozen cursor and milestone accumulation

- The initial request uses `afterSequence=0` and omits `asOfRevision`. Capture the
  first successful response's `lifecycleRevision` as `R`; every later load-more request
  in that traversal sends that exact `R` as `asOfRevision`.
- While the latest accepted response has `hasMore=true`, the next request uses that
  response's exact non-null `nextCursor` as `afterSequence`. Never derive a cursor from
  rendered length, activity time, gate state or another collection, and never switch to
  a newer revision during the traversal.
- Append/deduplicate behavior applies only to `milestones`. Preserve their received
  ascending order and use `sequence` as the sole milestone deduplication identity, so an
  overlapping or replayed sequence remains visible exactly once.
- While `hasMore=true`, keep the load-more affordance available and do not render or
  announce that complete history has been loaded. After an accepted response returns
  `hasMore=false`, issue no further page request from that traversal and do not invent a
  later cursor.

### Frozen full decision-gate snapshot replacement

- Every page response supplies the full current server-owned `decisionGates` snapshot.
  On each accepted page, replace/preserve gate state atomically as that one ordered
  29-entry collection; gate rows are never processed by milestone append or
  deduplication.
- Gate identity is exactly `(gateCode, requestedScopeKey)`. Preserve the server order:
  seven non-legacy `case:<caseId>` entries followed by 22 repeated
  `DG-LEGACY-FORM-CLASS` entries requested as `form-001` through `form-022`.
- Never append page snapshots into 58 or 87 gate rows, collapse the collection to the
  eight distinct gate codes, replace entries by code alone, retain stale first-page
  values when a later complete snapshot arrives, or discard gates after page one.
- Preserve every gate field from the latest accepted snapshot without calculation. In
  particular, an aggregate fallback remains requested as its individual `form-NNN` and
  may carry `resolvedScopeKey=ALL-22`; `ALL-22` is never rewritten as the requested
  scope and requested-form provenance is never lost.
- Pagination does not infer or recalculate business stage, official procedure stage,
  legal status, gate resolution, activation readiness, warning meaning or completeness
  from milestone contents. Those values remain the exact server-provided projection.

## Explicit Non-Closure

No backend change, second page capability or frontend business-state calculation. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): warnings; serialized

### Shared ownership serialization

- `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue` order key `3`; project this order only across owners present in the active manifest.
- `FRONTEND_TYPECHECK_VERIFICATION` order key `12`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01.md`
- `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts`
- `artifacts/FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Exact Playwright Acceptance

`FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts`
MUST prove through the existing case-detail three-lane overlay:

1. The first request sends `afterSequence=0` with no `asOfRevision`, captures response
   revision `R`, and renders its milestones in received ascending sequence order.
2. A three-page traversal sends page one's exact `nextCursor` and `R` on page two, then
   page two's exact `nextCursor` and the same `R` on page three; no request derives its
   cursor from rendered count and no request adopts a newer revision.
3. Fixtures with an overlapping/replayed milestone sequence across pages render the
   accumulated sequence list in order with each sequence exactly once. No gate or other
   snapshot collection participates in that append/deduplication path.
4. On each `hasMore=true` response, the load-more affordance remains available and no
   complete-history claim is visible. The first `hasMore=false` response ends the
   traversal without another request or synthesized cursor.
5. Every one of the three page fixtures contains a complete ordered 29-entry gate
   snapshot. After each load, the UI still has exactly 29 rows in that page's server
   order—not 58/87 rows, eight code-collapsed rows or a missing later-page collection.
6. Change a gate value/source field between the first and second complete snapshots and
   assert that the second snapshot replaces the stale value while all 29 composite
   identities remain. At least two legacy rows retain the same gate code with distinct
   requested form scopes.
7. Across all pages, assert the seven `case:<caseId>` identities plus ascending
   `form-001..form-022`; a fallback row keeps requested `form-NNN`, resolved `ALL-22`
   and its exact source provenance, and no row has requested scope `ALL-22`.
8. Server-provided lifecycle/gate labels remain unchanged when milestone fixtures vary,
   and a request spy observes only the expected overlay GET requests with zero POST,
   PUT, PATCH or DELETE requests.

The RED is missing multi-page cursor reuse, milestone-only accumulation, full gate
snapshot replacement or the `hasMore` completeness boundary. GREEN does not authorize
backend/adapter work, gate activation, a new state calculation or a second page feature.

## Verification Commands

- RED command: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-detail-overlay-cursor.spec.ts --workers=1`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-detail-overlay-cursor.spec.ts --workers=1`
- `cd frontend && npm run typecheck`
- `cd frontend && npx eslint src/modules/cases/components/CaseLifecycleOverlay.vue --max-warnings 0`
- `git diff --check -- frontend/src/modules/cases/components/CaseLifecycleOverlay.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-overlay-cursor.spec.ts tasks/postdemo/v8/FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01` pass. Only then may this task be reported PASS.
