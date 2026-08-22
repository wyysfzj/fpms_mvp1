# Story V8 Foundation Close Current Adoption

- Risk: `PROTECTED`
- Catalog ID: `FPMS-V8-FOUNDATION-CLOSE-20260712-01` (ordinal 280)
- Milestone: Foundation
- Candidate base: `312b078d437ec1b48d2a86cf823d4761218186b2`
- Outcome: independently close the C3.1 Foundation milestone from the current Git tree without
  reviving taskctl, old receipts, historical owner reconstruction or release execution.

## Exact closure

The frozen catalog contains 197 Foundation rows. Immediately before this self-close, the tracked
coverage ledger resolves 186 rows as `CURRENT_VERIFIED`, 10 rows as
`SUPERSEDED_BY_STORY` with current reviewed successors, and only this Row280 as `PENDING`.
The stateless lean checker validates catalog identity, commit reachability, exact story tree
fingerprints, latest integrated path ownership, observable tests and required PROTECTED reviews;
its Foundation run reaches only this deliberate self-pending row.

Row279 separately proves all 70 inherited Additional-Gap identities exactly once against their
current task contract or explicit successor and reruns the current integrated regression matrix.
No Foundation row relies only on historical prose, old taskctl state or ignored artifacts.

## Milestone verification

Fresh verification on the current candidate lineage produced:

- backend V8 matrix: `4643 passed, 24 skipped, 4 warnings, 114 subtests passed` in
  `1259.16s`; the 24 skips are only four C3-superseded control-plane modules;
- exact Row279 authority contract: `5 passed`, with scoped Ruff, format and diff checks passing;
- clean SQLite: one Alembic head `v8_d31_overlay_conflict_01`, upgrade from an empty database to
  head, development seed, idempotent second seed, and `alembic current` all succeeded under
  `PYTHONPATH=.` and a dedicated temporary database;
- frontend: repository ESLint, `vue-tsc --noEmit` and Vite production build all succeeded;
- real UI: isolated SQLite + FastAPI + Vite Playwright
  `v8-lifecycle-overlay-live.spec.ts` passed `1` test with real login, real API traffic, all three
  lifecycle/document/fee lanes, 401 activities across three pages, stable revision, 29 decision
  gates and no fulfilled application routes;
- inherited UI matrix excluding the contract-obsolete Task46 scenario passed `22` tests; the
  current real-stack successor above replaces its invalid generic-document auto-status premise;
- stateless inventory checker passed; the Foundation checker reached only this self-pending row.

The initial frontend milestone run exposed five compiler diagnostics with one common root: a
test-owned fee-preview contract globally shadowed the installed Axios instance with a stale narrow
interface. Commit `b2da6342c3fb4516981b0e8014023bccba473a23` removed only that augmentation.
All fee-preview assertions, including all 20 negative probes, stayed byte-identical; independent
High review approved P0/P1/P2 `0/0/0`; full lint/typecheck/build then passed.

The first Foundation checker also exposed three pre-existing ledger path-ownership omissions in
reviewed successor contracts. Commit `312b078d437ec1b48d2a86cf823d4761218186b2` records their
complete ancestry and exact fingerprints, plus the independently reviewed Axios correction.
Independent review approved those mechanical ownership corrections P0/P1/P2 `0/0/0`. No product,
contract or source-authority bytes changed in that commit.

## Safety and non-closure

Foundation preserves fail-closed legal status, official fee, deadline, evidence lineage,
permission and schema/migration rules. Customer/source decision lanes not eligible for Foundation
remain isolated for Full; no decision is inferred or activated. This close does not execute Full,
Final or Release, does not run the final release gate, and does not change product behavior.

The only unrelated worktree item is the pre-existing untracked `backend/uv.lock`; it is excluded
from this story and remains untouched. Temporary SQLite and server processes were isolated and the
FastAPI/Vite processes were stopped after E2E completion.

## Acceptance

An independent High reviewer must verify the exact report commit, current ledger eligibility,
test outputs, self-pending boundary and non-closure. After approval, the ledger may bind Row280 to
this story and the Foundation checker must pass terminally. The implementer cannot approve this
`PROTECTED` close.
