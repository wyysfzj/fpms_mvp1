# FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10

Status: ACTIVE
Risk-Class: PROTECTED
Outcome: The exact Integrated Scheme A candidate completes two fresh headed technical rehearsals and is accepted only for the frozen local synthetic demo scope.
Dependency: Task 9 exact candidate `579e8b50e51412e1ee468957854f6242f3f0343d`, independently APPROVED 0/0/0.

## Observable Outcome

Run only the focused checks owned by Tasks 2–9, then execute the canonical controller twice in
headed mode. Both runs must record IA-00…18 exactly once, 12 reviewed evidence bindings, disjoint
dynamic identities, screenshots, exact cleanup and the same final state:

- lifecycle `GRANT_REGISTRATION_IN_PROGRESS / GRANT_REGISTRATION / APPLICATION_PENDING / CONFIRMED`;
- legacy display `GRANT_PENDING`;
- bill `SETTLED / 0.00 CNY`;
- payment `FULLY_ALLOCATED / 0.00 CNY`.

The independent final High review binds this exact task-card commit/tree, all focused results and
both headed artifacts. The only permitted conclusion is `INTEGRATED_TECHNICAL_REHEARSAL_PASS`.

## Non-Goals

No product/source/test/controller changes, no customer-authorized runtime bundle activation, no
official-fee truth, public hosting, security, production/PostgreSQL, product-wide, release or broad
Playwright acceptance. This task does not claim product or release readiness.

## Expected Paths

- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-FINAL-REHEARSAL-20260821-01/**`
- `artifacts/FPMS-DEMO-INTEGRATED-A-FINAL-HIGH-REVIEW-20260822-01/HIGH_REVIEW.md`

## Tests

- focused backend tests for Tasks 2, 5, 6, 7, 8 and 9 plus scoped Ruff
- focused frontend contracts for Tasks 3, 4 and 8, typecheck and scoped ESLint
- canonical Integrated A static contract and one-test discovery
- `PYTHONPATH=/private/tmp/fpms-integrated-deps.HRGhrj:backend python3 scripts/run_demo_integrated_a_rehearsal.py --artifact /tmp/fpms-integrated-a-final --runs 2`

## Risk and Rollback

Risk is PROTECTED final demo acceptance. Rollback is this task-card commit only; generated runs use
disposable roots and exact cleanup. No stored customer or production data is created.

## Remaining Follow-Up Task IDs

None. Customer-authorized bundle activation, security, production and release remain separate
external/non-closure work and are not follow-up implementation tasks of this local rehearsal.
