# Story V8-PAYLIST-INTERNAL-EXPORT-SERVICE

- Risk: `PROTECTED`
- Outcome: generate an internal PayList `.xlsx`, persist its exact hash and managed
  artifact lineage, append one fee-lane activity per affected case, and return the bytes
  without claiming official upload or payment.
- Catalog ID: `FPMS-V8-PAYLIST-INTERNAL-EXPORT-SERVICE-20260712-01` (ordinal `160`).
- Base: `89d2686db34e3ff419e3a93300da80e78aadc666`.
- Authority: `docs/product/v8/domain-contract.md`,
  `docs/product/v8/source-decision-registry.md`, frozen catalog row `160`, its exact task
  contract, and the current PayList export-artifact carrier.

## Dependency and observable contract

The sole dependency,
`FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01`, is current-verified by
`V8-PAYLIST-EXPORT-CARRIER-CURRENT-ADOPTION` at commit
`fdb4bb56459050d61987fd68f6a953300fcaea94`.

The service accepts only the frozen command, renders the existing internal workbook,
stores one `INTERNAL_XLSX` artifact and content hash under managed storage, and appends
one `PAY_LIST_INTERNAL_EXPORTED` activity for each distinct sorted case. Exact replay
returns the same stored bytes and lineage. Conflicting replay, missing case scope,
invalid storage paths, symlinks, modified bytes, duplicate/malformed activities, or
partial write/append failure fail closed without claiming success. The caller owns the
database transaction.

## Exact paths and verification

- `backend/app/modules/annuity/service.py`
- `backend/app/modules/annuity/export_excel.py` (expected byte-unchanged dependency)
- `backend/tests/test_v8_internal_pay_list_export.py`
- `docs/product/v8/stories/V8-PAYLIST-INTERNAL-EXPORT-SERVICE.md`

The focused test is adopted byte-for-byte from archive ref
`6b2ef89da447353380b99853168d4d38aaf9210a` (Git blob
`7322dd5f7081ae8102a6831bfd506a0de3d4c90a`). The adopted service block is also
byte-identical to that archive slice (SHA-256
`ce2a221b6b03ec61592a55f3c76211c0e250aee96d2a61e1be9de6bd96957c3a`).

Fresh story-branch verification:

- RED: `pytest -q tests/test_v8_internal_pay_list_export.py` produced the expected
  `13 failed` because `ExportInternalPayListCommand`, `export_internal_pay_list`, and
  `get_settings` were absent.
- GREEN: the same focused command produced `13 passed`.
- Affected shared-service and carrier regressions produced `19 passed` across
  `test_v8_gov_payment_activity_adapter.py`,
  `test_v8_official_payment_evidence_activity_adapter.py`,
  `test_v8_internal_pay_list_export.py`, and
  `test_v8_pay_list_export_artifact_schema.py`.
- Scoped Ruff on the service and focused test passed.
- `git diff --check` passed.
- `backend/app/modules/annuity/export_excel.py` is byte-unchanged from the story base.

Affected shared-service regressions and the final exact commit-bound review are recorded
before integration.

## Non-goals and rollback

This story does not change the export-artifact schema, official upload, payment
acceptance, receipt verification, payment status, endpoint/API, UI, customer workbook
activation, migration/seed, official fee or reduction policy, row `125`, or successor
rows `161` and `162`. It does not modify or reinterpret the already-approved official
payment evidence adapter.

Rollback reverts the single story commit; the current artifact carrier and row125 adapter
remain intact.
