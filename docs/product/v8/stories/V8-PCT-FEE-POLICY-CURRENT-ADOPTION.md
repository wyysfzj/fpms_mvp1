# Story V8-PCT-FEE-POLICY-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Catalog ID: `FPMS-V8-PCT-FEE-POLICY-20260712-01` (ordinal 135)
- Runbook: `P0-prereq-heavy-story`
- Integration base: `60c35213c67218ff4c2f1664bbdc832e3f976a6c`
- Archive comparison anchor: `6b2ef89da447353380b99853168d4d38aaf9210a`
- Status: implemented and locally verified; independent acceptance remains required.

## Exact closure and authority

This story adopts only the current Delta-4 pure PCT national-stage fee policy. The exact
task appendix and Task 135 of the immutable Delta-4 freeze are latest-wins over the
superseded archive behavior.

- Task contract SHA-256:
  `1eb7e42125518e1e18ab09ad255fba37890e6edeef4046f8e1a7b694668a326b`
- Delta-4 freeze SHA-256:
  `7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8`
- Rule/source: `CN_PCT_NATIONAL_STAGE_POLICY_594` /
  `CNIPA_ANNOUNCEMENT_594_AND_ENTRY_NOTICE_20240806`
- Effective interval: `[2024-08-06, None)`

The command has exactly `case_id`, `fee_code`, `full_amount`, `effective_on`, `evidence`
and `reduction_context`. It has no `national_stage_entry_date`. The public evidence
validator has exactly `(case_id, effective_on, evidence)`.

## Adopted behavior

- Frozen reviewed CNIPA evidence is validated field-by-field, including exact case and
  current identity, lowercase SHA-256, issuer/role/final/review state, independent reviewer,
  naive review timestamp and `issued_on <= effective_on`.
- Exactly one RO receipt plus one ISR exempts only the five named application/excess/page
  fees. Exactly one ISR XOR one IPRP exempts only substantive examination.
- The six named reexamination/annuity fees require empty PCT evidence and delegate per-fee
  reduction to the accepted base or first-ten-year annuity validator.
- Unknown, foreign, late, duplicate, extra, conflicting or wrongly cardinalized evidence;
  unsupported/international/WIPO fee codes; and invalid/out-of-scope reduction fail closed.
- Amounts are positive finite Decimals with scale at most two. Exemption is exact `0.00`;
  other payable amounts use final-cent `ROUND_HALF_UP`, and ratios remain four-place exact.
- The implementation is pure: no persistence, rate-book read or activation, transaction,
  HTTP, I/O, clock, mutation, endpoint, seed or UI.

## Exact paths and current hashes

- `backend/app/modules/fees/pct_policy.py`
  - SHA-256: `52949de491be65258661fff2968c03b6958a998ca18c93c361243655057702de`
- `backend/tests/test_v8_pct_fee_policy.py`
  - SHA-256: `2a6301446400b6d80f57ed4abd37b568919b963a0f6109bd12fcd0c6c1a70728`
- `docs/product/v8/cutover-dirty-path-disposition.json`
  - SHA-256: `8fd6a873351744111791145bf997a0b73b6adebba2d7f6a9313537f8e7bae1cf`
- `docs/product/v8/stories/V8-PCT-FEE-POLICY-CURRENT-ADOPTION.md`

The disposition ledger changes only the two PCT path owners:
`V8-ADOPT-FEE-OBLIGATION` changes from `8` to `6`, and this story is added with count `2`.

## TDD and verification

The focused public-interface RED failed at collection with
`ModuleNotFoundError: app.modules.fees.pct_policy` (exit `2`). The interface-only GREEN
passed `1` test. The evidence/exemption tranche then produced the expected `32 failed,
1 passed`; its GREEN passed `33`. The domestic-reduction/Decimal tranche produced the
expected `20 failed, 44 passed`; the complete focused GREEN passed `69`.
A final latest-wins audit added a large finite Decimal case: it first failed `1` test
because of the archive-only storage ceiling, then passed after that ceiling was removed
and caller-independent Decimal precision was made magnitude-aware.

Fresh current-tree verification:

```text
pytest -q tests/test_v8_pct_fee_policy.py \
  tests/test_v8_fee_reduction_validator.py \
  tests/test_v8_annuity_first_ten_year_reduction_scope.py
194 passed

ruff check --no-fix app/modules/fees/pct_policy.py tests/test_v8_pct_fee_policy.py
All checks passed

python scripts/v8_lean_coverage_check.py --milestone inventory
PASS: V8 coverage ledger (inventory)
```

Exact four-path diff-check, commit-range inspection and hashes are required before handoff.
An independent High reviewer must review the exact commit/range and rerun the decisive
checks. The implementer does not approve this `PROTECTED` story.

## Non-goals and rollback

No superseded archive adoption, entry-date boundary, whole-case/whole-PCT flag, second
policy, rate lookup/activation, official amount, obligation, persistence adapter, endpoint,
HTTP mapping, schema/migration, seed, UI, customer decision, old task-control/evidence
mutation, Foundation claim or release claim is included.

Rollback reverts only the exact four paths above and returns the two disposition entries to
`V8-ADOPT-FEE-OBLIGATION` with its count restored from `6` to `8`.
