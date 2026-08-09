# Story V8-FORMAT-LETTER-REAL-TEMPLATE-SET-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Acceptance: `READY_FOR_INDEPENDENT_REVIEW` after the unchanged focused contract passed
  on the current tree.
- Outcome: adopt the integrated seed for the exact frozen eight-template dataset
  `FPMS-FORMAT-LETTER-CUSTOMER-20260610-V1`.
- Change mode: story only; no seed, focused-test or template byte changes.
- Catalog ID: `FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01` (ordinal `88`,
  profile `TC-SERVICE`).
- Authority: frozen row `88`, its exact task contract, and the document-lineage, source,
  seed and SQLite boundaries in the current V8 domain/source contracts.
- Historical comparison anchor: `83d014fb825c76e90c53821c7db9ed7f3cd49436`.
- Inspection base: `4af1414b24ee96e11c793fc2e2dec524dfa0d7ee`.

## Dependency, closure and exact paths

The sole prerequisite, `FPMS-V8-DE-REGISTER-VERSION-20260712-01`, is
`CURRENT_VERIFIED` through `V8-DOCUMENT-EVIDENCE-CORE-CURRENT-VERIFICATION`.

The current immutable catalog contains only `FORMAT_LETTER_001` through `_008`, with the
frozen source hashes, names, mapping patterns, version IDs, paths and variable sets. Seed
validation precedes mutation; missing, invalid, placeholder, wrong-variable and ambiguous
carriers fail closed. A clean seed creates the exact eight Templates and mappings, a
completed second run returns zero, reusable IDs and caller-owned transaction semantics are
preserved, and unrelated/manual rows remain untouched.

Exact row-owned paths are:

- `backend/scripts/seed_dev.py`;
- `backend/tests/test_v8_format_letter_real_template_set.py`; and
- `backend/storage/templates/format_letters/format_letter_001.docx` through
  `format_letter_008.docx`.

The focused-test blob (`8c18682a8c155198e2ecc8cc1acca58504b0d242`) and all eight
template blobs are byte-identical to the historical anchor. The seed’s row-88 hunk is
unchanged; its complete file differs from the anchor only in two later official-notice
activation lines outside this closure.

## Current verification and resolved environment stall

Read-only inspection passed for all eight customer source hashes, OOXML packages, exact
variables, A4 landscape sections, table/header/cell structure and prohibited markers.
Scoped Ruff check-only passed.

The earlier released SQLite run returned `13 passed, 1 failed, 1 warning`; every
dataset/seed assertion passed, while the frozen LibreOffice DOCX-to-PDF batch reached its
unchanged 60-second timeout. One cold selector retry reproduced that timeout. The exact
inherited command independently returned `7 passed, 3 warnings`.

On 2026-08-09 the controller diagnosed the external runtime without changing repository
bytes: a single committed DOCX converted successfully, the exact ten rendered variants
then converted as one batch, and the first `pdfinfo` process showed the same cold-runtime
delay before subsequent invocations returned normally. With both unchanged external
binaries initialized, the exact focused command completed with `14 passed, 1 warning in
7.13s`. This supersedes the environment-only `TRUE_STALL`; seed, focused-test and all eight
template blobs remain byte-identical to the historical anchor. Independent High review is
still required before current-tree adoption.

## Non-goals and rollback

No ninth mapping, second dataset, new customer wording, API/UI/schema/migration, context,
renderer/archive/email behavior, calculation rule, fallback, customer-decision activation,
adjacent seed cleanup, ledger/review edit, historical task/evidence mutation or Foundation
claim. Rollback removes only this story card.
