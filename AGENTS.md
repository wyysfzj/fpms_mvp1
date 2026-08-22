# AGENTS — FPMS Lean 5.6 Delivery Rules

Authority descends from current system/developer/user instructions to this file, then to `docs/product/v8/domain-contract.md`, `docs/product/v8/source-decision-registry.md`, the current story card, `docs/product/v8/coverage-ledger.json`, approved V8 designs, and code.
Lower authority cannot weaken higher authority. Missing legal, customer, source, fee, deadline, lineage, permission, or migration authority fails closed only for the affected lane.

## Delivery

- Work from an isolated Git worktree and one observable story outcome.
- The story card defines outcome, non-goals, catalog IDs, source/decision references, dependencies, expected paths, tests, risk class, and rollback boundary.
- Implement the minimum exact change; no adjacent cleanup, renaming, reformatting, speculative abstraction, or unrelated compatibility work.
- New behavior and bug fixes use targeted RED → minimum GREEN → affected regressions → scoped lint/type/diff. Do not delete correct work to manufacture RED.
- Commit SHA/range is scope and durable checkpoint. A byte-changing rebase, cherry-pick, merge conflict, or later override invalidates prior verification and review.
- Old `docs/agents/**`, `scripts/taskctl`, canonical scope, owner, candidate, and evidence machinery are read-only history; do not extend them or use them to close new stories.

## Risk and review

- `PROTECTED`: lifecycle/legal status, deadlines, official fees, fee reduction, payment, service receivables, document/evidence lineage, auth/security, schema/migration/seed, SQLite, customer decisions, source activation, milestones, and unknown/mixed risk.
- `NORMAL` is frozen API/UI/adapter work that changes none of those semantics; `MECHANICAL` has no runtime, product, or authority semantics.
- Implementers cannot approve their own `PROTECTED` work. An independent High reviewer reviews the exact commit/range and independently reruns decisive checks.
- `NORMAL` stories may share one independent per-wave review with a per-story verdict.
- Concurrent stories may not edit the same source, test, migration, schema, router, shared registry, or shared ownership file.
- Migrations, SQLite-writing tests, shared hot files, milestone verification, and release checks are serialized. Default to at most two implementation lanes.

## Product and release invariants

- Preserve every fail-closed rule in the domain and source contracts.
- New or changed visible UI text is Simplified Chinese. Preserve API status, envelope, permission, transaction, and error semantics.
- Do not run repo-wide tests, full frontend build, broad Playwright, or release checks before their named milestone. Release is always last.
- Every catalog row resolves through the coverage ledger to a current reachable commit, observable test, disposition, and required independent review.
- Historical PASS, summaries, receipts, and archive checkpoints are evidence inputs, not current integrated-tree acceptance.

## Recovery and safety

- On disconnect, inspect branch, status, commits, processes, reviews, and ledger; resume from the first incomplete step without repeating durable work.
- An agent is stalled only after two negative observations at least 30 seconds apart and at least 90 seconds without process, diff, commit, log, or message progress.
- Preserve quarantine and archive refs. Do not push, reset, clean, stash, discard user changes, expose secrets/PII, or run destructive data operations unless the user explicitly changes those boundaries.
