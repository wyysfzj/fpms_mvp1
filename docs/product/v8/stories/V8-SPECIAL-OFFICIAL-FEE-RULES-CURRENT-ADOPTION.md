# Story V8-SPECIAL-OFFICIAL-FEE-RULES-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Initial implementation base: `dfc312b4fde48872ebb11b940167fa0cbc0f8bb2`.
- Current integration parent for final review:
  `d421516d286d16d5521c469b30c53b9be039ce60`.
- Outcome: current-adopt exactly catalog rows 136–145: seven layout-design fee rules,
  the patent-term-compensation request fee rule, the compensation-period annuity rule,
  and the open-license annuity reduction rule.
- Authority: the ten exact frozen task files, the row-136 Delta-4 latest-wins appendix,
  the current special-fee design, the accepted D4-09 candidate at `82bc4f7`, and the
  accepted annuity-reduction dependency at `1a289152`.
- Change mode: focused public tests adopted byte-for-byte from archive checkpoint
  `6b2ef89da447353380b99853168d4d38aaf9210a`, followed by minimum current-tree
  implementation and fresh targeted TDD.

## Catalog rows and observable outcomes

1. Row 136, `FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01`:
   read exactly one approved, active and effective `CNIPA_LAYOUT_246` book and its exact
   linked `IC_LAYOUT_REGISTRATION_FEE=1000.00 CNY` rate. The read validates the complete
   source snapshot/hash, immutable book/rate state and amount without writing.
2. Row 137, `FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01`:
   `IC_LAYOUT_REEXAM_REQUEST_FEE=1000.00 CNY`.
3. Row 138, `FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01`:
   `IC_LAYOUT_RESTORATION_REQUEST_FEE=500.00 CNY`.
4. Row 139, `FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01`:
   `IC_LAYOUT_BIBLIOGRAPHIC_CHANGE_FEE=50.00 CNY`.
5. Row 140, `FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01`:
   `IC_LAYOUT_EXTENSION_REQUEST_FEE=150.00 CNY`.
6. Row 141, `FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01`:
   `IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUEST_FEE=150.00 CNY`.
7. Row 142, `FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01`:
   `IC_LAYOUT_NONVOLUNTARY_LICENSE_REMUNERATION_ADJUDICATION_FEE=150.00 CNY`.
8. Row 143, `FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01`:
   `CN_PATENT_TERM_COMPENSATION_REQUEST_FEE=200.00 CNY` on and after `2024-08-06`.
9. Row 144, `FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01`:
   exact `8000.00 CNY` per nonnegative complete year on and after `2024-07-26`, including
   zero for no complete year and no partial-year inference.
10. Row 145, `FPMS-V8-OPEN-LICENSE-ANNUITY-REDUCTION-RULE-20260712-01`:
    compare the exact `0.15` open-license reduction with an accepted existing
    `0`, `0.7` or `0.85` ratio, apply only the greater benefit and never stack ratios.

Every command and result is an immutable slots dataclass. Invalid command/type/date/year
or ratio inputs fail with the rule's exact 400 error. The pure fixed rules perform no
database, clock, I/O or mutation behavior.

## Exact paths

- `backend/app/modules/fees/official_rate_book.py`
- `backend/tests/test_v8_layout_registration_fee_rule.py`
- `backend/tests/test_v8_layout_reexamination_fee_rule.py`
- `backend/tests/test_v8_layout_restoration_fee_rule.py`
- `backend/tests/test_v8_layout_bibliographic_change_fee_rule.py`
- `backend/tests/test_v8_layout_extension_fee_rule.py`
- `backend/tests/test_v8_layout_nonvoluntary_license_fee_rule.py`
- `backend/tests/test_v8_layout_remuneration_adjudication_fee_rule.py`
- `backend/tests/test_v8_term_compensation_request_fee_rule.py`
- `backend/tests/test_v8_compensation_period_annuity_rule.py`
- `backend/tests/test_v8_open_license_annuity_reduction_rule.py`
- `docs/product/v8/cutover-dirty-path-disposition.json`
- this story card.

The ten focused tests retain exact archive Git blobs:

- registration `316860dc1604e922a3e9b1adef056230d234af18`;
- reexamination `5f26e237b9f6b3636bb34ec5f85e3569843333fb`;
- restoration `b9cd077dade52e6d0002d56013957f9d3212dfd0`;
- bibliographic change `79ab87889c175f05373ec38453bacbe505d90f16`;
- extension `13efb6bd1c1f10daa373abb840145b49b47f3dfe`;
- nonvoluntary license `98ae1647540b88a0c80cb0bfc8ca1941fc66c3a9`;
- remuneration adjudication `d752389fe08828042414dcff914317bad81a0095`;
- term-compensation request `c6c777d9ff4608f83efc9f4f4d5a842340dd4452`;
- compensation-period annuity `151103c9791720bf4f5f4786b564e55d629d3a7b`;
- open-license reduction `6031a2172e0484dc75e34936001e7153f27764c0`.

## TDD and verification

The registration test was adopted first while `official_rate_book.py` remained unchanged.
The exact serialized RED exited `1` with `27 failed, 1 warning in 7.57s`; the decisive
failure was the missing `GetLayoutRegistrationFeeCommand`,
`GetLayoutRegistrationFeeResult` and `get_layout_registration_fee` public boundary.

After the minimum registration reader and each remaining test/rule pair were added
sequentially, the one authorized combined exact ten-file GREEN exited `0` with
`60 passed, 1 warning, 89 subtests passed in 15.51s`.

The registration test is also the smallest carrier/source dependency regression: it
materializes the accepted D4-09 candidate, activates it through
`activate_official_rate_book()`, validates the exact source-bound persisted graph and
proves repeated read-only access. The two-run SQLite serialization contract therefore
requires no additional SQLite tranche.

Scoped Python compilation, Ruff check and Ruff format-check are required on the exact
product and ten tests. Exact inventory, archive test identity, row-135 non-absorption,
diff check and hashes are required before handoff. The implementer does not approve this
`PROTECTED` story; an independent High reviewer must review and rerun the exact candidate.

## Shared ownership, non-goals and rollback

After the independently accepted row-135 PCT story was integrated, the controller
serialized the shared cutover disposition correction. Exactly the product path and ten
focused-test paths move from `V8-ADOPT-ANNUITY-RATE-SOURCES` to this story; the former
count changes from `31` to `20` and this story is added with count `11`. The exact
current disposition SHA-256 is
`23412b81d16d876d6a3581cab36c6932bb132e310a25f4f04f2075422c1b7d49`.
All 474 paths remain unique and reconcile. Coverage ledger, review receipt and source
registry remain unchanged in the candidate.

Catalog row 135 is a current predecessor but its PCT DTOs/functions/tests are unchanged
and excluded from this story. `get_active_layout_reexamination_fee`,
obligation/provider adapters, candidate materialization or mutation, activation changes,
schema, migration, seed, API, UI, customer data, other fees and release/milestone closure
are excluded.

Rollback reverts the one product-file rule slice, ten focused tests, exact eleven-path
disposition ownership/count correction and this story card. It leaves the accepted
candidate, PCT policy, source files, carrier and active-book state unchanged.
