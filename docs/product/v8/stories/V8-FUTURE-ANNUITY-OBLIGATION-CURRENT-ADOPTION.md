# Story V8-FUTURE-ANNUITY-OBLIGATION-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Product/test commit: `807c93e0d389e05f4c620c287d8eed17a74b2f83`
- Outcome: current-adopt the frozen sourced Future Annuity obligation seam on the lean
  integrated tree.
- Catalog ID: `FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01` (ordinal `133`).
- Authority: the task's Delta-4 latest-wins appendix, the user-approved Delta-12 Future
  Annuity contract, and Delta-27 sections 5–7.
- Historical product checkpoint: `6b2ef89da447353380b99853168d4d38aaf9210a`.

## Current prerequisites and exact paths

- D4-10 CNIPA annuity rate candidate: current-adopted at `4af1414`.
- D4-11 six-field task-to-obligation carrier: current-adopted at `cb34955`.
- Delta-27 durable reduction-lineage carrier: product commit `03585cb`, current adoption
  `cf060d1`.
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_future_annuity_obligation.py`

## Observable contract

The exact typed seam validates the eleven command facts, the grant-announcement source and
evidence lineage, accepted post-grant projection, active approved effective D4-10 rate,
strict canonical tier, and exact annuity reduction approval coverage. It delegates exactly
once to generic obligation recognition, preserves the full annual fee as the late-fee base,
keeps the initial instruction pending, and atomically writes the six-field D4-11 carrier
and one immutable Delta-27 reduction-lineage row.

Exact replay runs before mutable current-source, rate and approval checks. It compares the
durable task, obligation, line and reduction-lineage facts and returns the original rows
with `reused=True`; drift or corruption fails closed under the frozen 400/404/409 error
partition. The caller owns the transaction and the seam performs no commit or rollback.

## Verification, non-goals and rollback

The unchanged approved 897-line focused test first produced the expected RED (`27 failed`)
because the public seam was absent. After reconciling only the archived Task-133 service
hunk with the current prerequisite APIs, focused SQLite verification passed `27/27` with
one inherited passlib `crypt` deprecation warning. Scoped Ruff check-only and exact diff
check passed.

No rate/source activation or seed, D4-10/D4-11/Delta-27 carrier change, Task-121 instruction
adapter, generic fee-service change, API/UI, task/ledger/review/evidence update, or unrelated
cleanup is included. Rollback removes this story and the Task-133 service/test adoption;
all current prerequisite carriers and rate-candidate state remain unchanged.

Independent High review approved the exact product commit with P0/P1/P2 `0/0/0` after
rerunning the focused SQLite test (`27 passed`), scoped Ruff and exact diff checks. A
separate successor tranche for the six pre-existing annuity-service consumers passed
`26/26`.
