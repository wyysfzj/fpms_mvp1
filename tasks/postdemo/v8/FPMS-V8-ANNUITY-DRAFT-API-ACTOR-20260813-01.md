# FPMS V8 Annuity Draft API Actor

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

The authenticated annuity draft endpoint must pass the server-owned user id to the reviewed draft
adapter and own the request transaction: one commit on success, one rollback on service or commit
failure. The client cannot supply or override the actor.

## Exact RED and closure

After a task obtains reviewed obligation lineage and a `PAY` instruction, the current endpoint
still returns per-item `FEE_OBLIGATION_DRAFT_COMMAND_INVALID` because it calls the adapter without
`actor_id`; it also closes the request without committing the adapter's caller-owned writes. The
focused RED requires the exact authenticated actor and transaction behavior. The minimum closure
adds `current_user_dep`, forwards only `current_user.id`, and wraps the existing call in
commit/rollback.

## Non-closure

- No service, obligation, rate, reduction, instruction, PayList, payment, UI, schema, migration,
  seed, inherited-test or Row283 change.
- No client actor field, fallback actor, internal service commit, permission change, error remap,
  monkeypatch in production, skip, xfail or assertion deletion.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-ANNUITY-DRAFT-API-ACTOR-20260813-01.md`
- `backend/app/modules/annuity/api.py`
- `backend/tests/test_v8_annuity_draft_api_actor.py`

## Verification and acceptance

Run the focused API test and the authoritative annuity draft-obligation adapter suite. Run scoped
Ruff and exact diff-check. Independent High review must approve P0/P1/P2 `0/0/0` before inherited
annuity alignment resumes.

## Current verification result

RED completed with two exact failures: the adapter mock could not receive the missing authenticated
actor, and a service exception caused zero rollbacks. Final focused API plus authoritative adapter
verification completed `8 passed` in `3.72s`, with four pre-existing dependency/deprecation
warnings. Scoped Ruff and exact diff-check pass.
