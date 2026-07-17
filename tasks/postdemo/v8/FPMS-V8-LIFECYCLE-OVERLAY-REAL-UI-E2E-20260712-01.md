# FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-14 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `17. Wave 8 — real paths and release close`
Catalog ordinal: `276`
Executor role: Tester / monitor

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `821`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low — this task owns one dedicated Playwright specification and no shared product file.
- `prereq_dependency_density`: high — the real-stack proof requires the dedicated live fixture and its completed overlay/UI chain.
- `be_fe_coupling`: high — one browser flow crosses real authentication, FastAPI, SQLite-backed overlay data and the Vite UI.
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: The exact real-stack Playwright fails when any lane, stable-page cursor, composite gate identity or reference-only presentation is absent, or when route fulfillment substitutes for the live path.
- GREEN expectation: The exact serialized one-worker Playwright passes through real login/API/Vite with the complete three-page, three-lane and 29-gate assertions below.

## Exact Closure Slice

Real login/API/Vite case path, no route fulfillment, verifies three lanes and stable three-page cursor.

## Ultra Contract Freeze — 2026-07-14 (delta-2)

This section is authoritative for High implementation. It freezes only the existing
real-stack lifecycle-overlay E2E proof against the dedicated live fixture. It does not
add another fixture, page capability, product repair or customer-policy decision.

### Real-stack and no-fulfillment boundary

- Exercise the actual Vite-served login and case-detail UI, the real authentication and
  lifecycle-overlay FastAPI endpoints, and the SQLite data prepared by
  `FPMS-V8-LIVE-FIXTURE-20260712-01`. Do not replace UI navigation or API reads with a
  direct test-only response path.
- No Playwright page/context route handler may fulfill authentication, case, overlay,
  milestone or decision-gate responses. Passive request/response observation is allowed,
  but `route.fulfill()` or any equivalent mock-only success path cannot satisfy this
  task.
- Fixture setup/teardown and the browser traversal share the global serialized SQLite
  fixture queue. The Playwright command uses exactly one worker and must not overlap
  another SQLite-writing verification.

### Composite gates across the stable three-page traversal

- Every one of the three real overlay responses contains exactly 29 distinct composite
  identities `(gate_code, requested_scope_key)`: seven non-legacy gate codes requested
  at `case:{case_id}`, followed by 22 `DG-LEGACY-FORM-CLASS` entries requested at
  `form-001` through `form-022`.
- The repeated legacy gate code remains 22 separate visible entries. A code-only set has
  eight values while the composite-key set has 29; the E2E must fail if the UI collapses,
  replaces or omits any repeated-code row.
- At least one fallback entry visibly preserves its requested `form-NNN` together with
  `resolved_scope_key=ALL-22` and source provenance. No entry is requested as `ALL-22`.
- At least one unresolved entry remains visible with its requested scope and reason. It
  must not block the other 28 entries, any center/document/fee lane, or later milestone
  pages.
- The complete ordered gate snapshot is identical across the stable three-page cursor
  traversal and remains 29 visible rows after every load; it is not appended to 58/87
  rows, code-deduplicated or dropped after page one. Milestones alone paginate using the
  first response revision and each exact next cursor, accumulating their three pages
  without changing the gate snapshot.
- Live legacy rows classified `HISTORICAL` or `INTERNAL_ONLY` visibly retain the exact
  Simplified-Chinese reference-only markers `仅供参考` and `非激活`. A reference-only
  warning uses `仅供参考`; none of these labels implies activation.

## Explicit Non-Closure

No product fix, schema change or test-assertion weakening. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LIVE-FIXTURE-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): live fixture

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.
- The live fixture seed/reset and this Playwright traversal execute in that queue as one
  serialized real-stack verification; Playwright remains `--workers=1`.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts`
- `artifacts/FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Follow the frozen foundation/full close order; QA tasks report failures and never repair product code.

## Exact Real-Stack Playwright Acceptance

`FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts`
MUST prove:

1. A user signs in through the real Vite UI, reaches the real seeded case-detail route,
   and receives the overlay from FastAPI/SQLite without fulfilled application routes.
2. The center, document and fee lanes all render from the live fixture before and after
   load-more actions.
3. Each of the three response snapshots and the rendered gate collection has the exact
   ordered seven case-scoped plus 22 form-scoped composite identities; the repeated
   legacy code is not collapsed.
4. A fallback row shows requested `form-NNN`, resolved `ALL-22` and its source fields,
   while no row has requested scope `ALL-22`.
5. An unresolved row remains visible while other resolved rows, all three lanes and the
   full traversal continue normally.
6. Page two and page three reuse the first revision and exact preceding cursor;
   milestones advance across three pages while the complete 29-entry gate snapshot stays
   identical and visible after each load.
7. The live reference-only classifications/warning show the exact Simplified-Chinese
   labels `仅供参考` and `非激活`, with no activation control or mutation.
8. Passive network observation confirms real login/case/overlay traffic and no
   Playwright route fulfillment supplies application data.

The RED is any missing named real-path assertion, composite-identity loss, unstable gate
snapshot or fulfilled application response. GREEN does not authorize product repair,
fixture changes, mock-only coverage or another E2E scenario.

## Verification Commands

- RED command: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-lifecycle-overlay-live.spec.ts --workers=1`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-lifecycle-overlay-live.spec.ts --workers=1`
- `git diff --check -- FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts tasks/postdemo/v8/FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01` pass. Only then may this task be reported PASS.
