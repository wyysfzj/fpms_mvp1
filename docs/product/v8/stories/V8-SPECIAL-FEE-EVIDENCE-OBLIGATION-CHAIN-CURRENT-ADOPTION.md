# Story V8-SPECIAL-FEE-EVIDENCE-OBLIGATION-CHAIN-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `98225b3b6e4c108750477cfe0d105ce15d961fd7`
- Outcome: current-adopt the ordered catalog chain 146–154, converting independently
  reviewed final evidence into exact special official-fee obligations.
- Authority: the nine frozen task files, their current-verified review/finalize and
  recognize-obligation dependencies, and the accepted special fee rules at `5211b1b`.
- Change mode: adopt the nine focused public tests from the quarantine archive, preserve
  one contract-complete RED, then port only their required current-tree service slices.
  The row-147 test receives one exact latest-wins compatibility correction from the
  superseded active-book reader to the accepted pure reexamination fee rule.

## Ordered catalog outcomes

1. `IC_LAYOUT_REGISTRATION_FILED` recognizes only the active
   `IC_LAYOUT_REGISTRATION_FEE`, with `fee_year_key=0`.
2. `IC_LAYOUT_REEXAM_REQUESTED` recognizes only
   `IC_LAYOUT_REEXAM_REQUEST_FEE`; rejection or a possible request does not trigger it.
3. `IC_LAYOUT_RESTORE_RIGHT_REQUESTED` recognizes only
   `IC_LAYOUT_RESTORATION_REQUEST_FEE`; a loss-of-right notice alone does not trigger it.
4. `IC_LAYOUT_BIBLIO_CHANGE_SUBMITTED` recognizes only its own
   `IC_LAYOUT_BIBLIO_CHANGE_FEE`.
5. `IC_LAYOUT_EXTENSION_REQUESTED` recognizes only
   `IC_LAYOUT_EXTENSION_REQUEST_FEE`; a deadline alone does not trigger it.
6. `IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUESTED` recognizes only
   `IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUEST_FEE`.
7. `IC_LAYOUT_REMUNERATION_ADJUDICATION_REQUESTED` recognizes only
   `IC_LAYOUT_NONVOLUNTARY_LICENSE_REMUNERATION_ADJUDICATION_FEE`.
8. `TERM_COMPENSATION_REQUESTED` recognizes only
   `CN_PATENT_TERM_COMPENSATION_REQUEST_FEE`; the request date is the source date and an
   absent official due remains blocked.
9. `TERM_COMPENSATION_GRANTED` records a review-bound source snapshot and recognizes one
   `CN_COMPENSATION_PERIOD_ANNUITY_FEE` line per complete year, no partial-year line, and
   fails closed when the exact period/full-year facts are missing.

Every adapter accepts only same-case, current, independently reviewed final evidence and
its exact activity/evidence carrier. Replay is exact and idempotent. Conflicts write
nothing. `recognize_obligation` owns the sole fee activity and the caller owns the
transaction.

## Exact story paths

- `backend/app/modules/documents/evidence_service.py`
- `backend/app/modules/documents/fee_linking_service.py`
- `backend/tests/test_v8_ic_layout_registration_filed_obligation.py`
- `backend/tests/test_v8_ic_layout_reexamination_request_obligation.py`
- `backend/tests/test_v8_ic_layout_right_restoration_request_obligation.py`
- `backend/tests/test_v8_ic_layout_bibliographic_change_submission_obligation.py`
- `backend/tests/test_v8_ic_layout_extension_request_obligation.py`
- `backend/tests/test_v8_ic_layout_nonvoluntary_license_request_obligation.py`
- `backend/tests/test_v8_ic_layout_remuneration_adjudication_request_obligation.py`
- `backend/tests/test_v8_patent_term_compensation_request_obligation.py`
- `backend/tests/test_v8_compensation_period_annuity_obligation.py`
- `docs/product/v8/cutover-dirty-path-disposition.json`
- this story card.

Eight tests retain their exact quarantine SHA-256 values; the row-147 current-tree hash
is recorded after its one compatibility correction:

- registration `11a9b2f8933c43fbe4745e4997e87a7ee7131b5d944815267774fae108fe9ca2`;
- reexamination quarantine source
  `87968badf533be2751c5856932f3b3065cc1736f165d201d21c1ea2a49c7a24b`;
  current corrected test
  `b1e8e9e865ccee37ebf5529ca40a18272e65191fa573a037a7025fd655afaec0`;
- restoration `c4e9aea5a452877541c8b42a88e5cd22df65886da889bd90cb090bdd787778a4`;
- bibliographic change `6ab133eb370b33b907e2d42714c0822b66a954a2663180c56bc4559ff4e729e1`;
- extension `74a90777613446296962e82d24f238c4a4f43e83910b3f108e71b9330d1e69ca`;
- nonvoluntary licence `ab1fa4f678d673e3b59656e56014f13a9a737fed43fd757f5a7bb259c5f25e63`;
- remuneration adjudication `bb5cf375a4383589a49ddfdf4f992de468760b79ad4d0d6e4794fa3ca202004c`;
- term compensation request `b4748670350a1d0e0d2bba9ac7f3e58b6d57a631fabc9d8f0b1cafb0018f03d0`;
- compensation-period annuity `2e38802faa1fb1b35c01a285eadb0a6503d5d9a6fc8630cf1037834bee82c03f`.

## Verification and non-goals

Run the exact nine-file SQLite tranche serially for RED and canonical GREEN, followed by
affected review/finalize, fee-rule and obligation-core regressions, scoped Ruff and exact
diff/inventory checks. The implementer does not approve the story; an independent High
reviewer reviews the exact commit and reruns the decisive tranche.

The contract-complete RED exited `1` with `91 failed` and `52 skipped`, proving all nine
public adapter/review boundaries absent. After the minimum current-tree port, the exact
nine-file GREEN passed `143` tests. Following scoped format/lint, the canonical combined
adapter plus document-review/finalize and obligation-core regression tranche passed
`424` tests. The row-147 compatibility correction removes the superseded
`get_active_layout_reexamination_fee` dependency and delegates to the accepted pure
`get_layout_reexamination_fee` rule.

The disposition transfer moves two source paths from `V8-ADOPT-DOCUMENT-EVIDENCE` and
nine tests from `V8-ADOPT-ANNUITY-RATE-SOURCES` to this story. The former counts become
`28` and `11`; this story owns `11`; all `474` paths remain unique. The exact disposition
SHA-256 is
`175d83d3e5626a6b6713e2ebbacebe41d0731696ee27d1f5aafa932f08183ef3`.

Row 155 open-licence annuity obligation remains outside this story because its future
annuity obligation dependency is not current-verified. No ordinary annuity creation,
payment, PayList, receivable, API, UI, schema, migration, seed, source activation, new
entrypoint, unrelated evidence flow, or adjacent refactor is included.

Rollback removes only the nine adapter/review slices, nine focused tests, exact
disposition ownership transfer, and this story card. It leaves the underlying fee rules,
review/finalize services, obligation core, active rate book, and all prior stories intact.
