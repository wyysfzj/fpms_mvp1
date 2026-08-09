# Story V8-FORMAT-LETTER-CONTEXT-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: build one immutable, reviewed context for a real format-letter template from
  the explicitly selected latest official incoming document.
- Catalog ID: `FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01` (ordinal `89`).
- Product commit: `8f87c9f92ff69e4677d5ed00f2269f7d634dc378`.

## Observable contract

The read-only service accepts only the frozen typed command and the caller-owned database
session. It binds the named case and incoming document to exactly one current approved
official-PDF evidence version, requires that document to be the deterministic latest
eligible incoming source, and selects one enabled mapping by the frozen exact precedence.

The selected mapping must resolve to one enabled real `FORMAT_LETTER_001..008` template.
The source title and template identify exactly one approved notice variant, including the
first/subsequent OA and reexamination split. Applicant, inventor, contact, salutation and
case fields follow the frozen deterministic precedence. Deadline-bearing variants accept
only a confirmed imported or manually captured official deadline. The grant-registration
variant additionally binds one effective verified GOV obligation with CNY lines and the
same due date. Missing, ambiguous, stale, unreviewed, conflicting or unsupported data
fails closed with the task-owned typed business error.

The result contains only strings in a fresh immutable mapping and preserves the reviewed
source evidence, mapping, template, contact-selection and notice-variant identities. The
builder performs no render, attachment/evidence/handoff write, transaction control, clock
read, identifier generation or fallback inference.

## Verification and review

With the exact archived focused test restored before the implementation module, the RED
was `45 failed`, all at the missing module boundary. Restoring the exact reviewed archive
implementation produced `45 passed`. The frozen inherited filename
`test_v8_document_evidence_review.py` is absent from both the current tree and archive;
its current `review_service` and `review_api` replacements plus the remaining named
contract, current-version, template-set, mapping-seed and handoff API regressions passed
`116` tests.

Scoped Ruff, format and exact diff checks passed. Independent High review approved the
exact product commit with `P0/P1/P2 = 0/0/0`. The product and focused test blobs are
byte-identical to the preserved archive reference.

## Non-goals and rollback

No rendering, generated document, archive/handoff write, endpoint/UI/schema/migration,
email, generic template engine, customer-policy inference or second catalog row is
included. Rollback reverts the product commit and this adoption record; the independently
accepted real template set and document/evidence prerequisites remain intact.
