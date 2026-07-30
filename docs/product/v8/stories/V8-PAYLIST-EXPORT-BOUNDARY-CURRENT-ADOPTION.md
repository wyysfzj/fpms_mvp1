# Story V8-PAYLIST-EXPORT-BOUNDARY-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Base: `a43075e7890fe10dc3bad388f190e0110484ddf1`
- Outcome: keep payment evidence, internal export artifacts and official workbook state
  separate in PayList write/read behavior.
- Authority: frozen catalog rows 161 and 162, their exact task contracts, and the current
  PayList internal-export and export-artifact carrier stories.
- Change mode: exact task-patch adoption from the preserved pre-Lean archive, followed by
  current Ruff normalization, fresh current-tree regression and independent High review.

## Catalog IDs

1. `FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01` (ordinal `161`)
2. `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01` (ordinal `162`)

## Durable state and exact scope

- Both rows preserve historical RED, GREEN and terminal independent PASS; historical RED
  is not rerun.
- Exact product path: `backend/app/modules/annuity/service.py`.
- Exact decisive tests:
  - `backend/tests/test_v8_pay_list_payment_export_decouple.py`
  - `backend/tests/test_v8_pay_list_export_artifact_read.py`
- Row 161 test remains exact archive blob
  `150572fa1024b821f9765167ac45e392d6459e20`.
- Current Ruff normalizes the row 162 test to
  `8a81afde52206090c0d236d843fb2afd043f401c`; the adopted service becomes
  `931ff352cad78cb4cdf3f3a22c8fe99c01bdb465`.

## Observable behavior

- `mark_pay_list_paid` relies on persisted payment evidence for every payment row; it no
  longer requires an internal or official export status as a prerequisite.
- Existing `EXPORTED` rows remain readable. Internal export never proves payment and
  payment never proves official workbook acceptance.
- PayList detail returns the header, payment facts, internal export artifacts and official
  workbook metadata as separate projections under `no_autoflush`.
- Export artifacts are ordered deterministically. Official workbook fields are emitted
  only when persisted and are not inferred from internal artifact or payment state.

## Verification and successor boundary

- Fresh combined tranche with rows 159–162 and payment-evidence activity regressions:
  25 passed.
- Scoped Ruff, Ruff format-check and diff-check passed.
- The row 160 internal-export seam and row 125 payment-evidence activity remain current.
- The archive's later Future Annuity implementation is not adopted or claimed.
- An independent High reviewer must review the exact commit, rerun decisive checks and
  reattest the current internal-export and payment-evidence successors.

## Non-goals and rollback

No endpoint/UI/schema/migration, payment fabrication, official workbook generation or
acceptance, future-annuity behavior, fee rule, source activation, customer default,
adjacent annuity cleanup, old evidence mutation, ledger edit or milestone claim. Rollback
reverts only this story commit.
